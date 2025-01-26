import numpy as np
import pandas as pd
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from sklearn.preprocessing import MinMaxScaler, StandardScaler

import CreateDeepLearningModel as dl_model
import PreprocessingData as pre_process

import tensorflow as tf
from tensorflow.keras.backend import clear_session

import os
from pathlib import Path
from datetime import datetime

import Utils as utility_function

import logging

# Configure logging
date_today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_directory = 'outputs/logs/'
utility_function.ensure_directory_exists(log_directory)  # Ensure the log directory exists
filename = f'{log_directory}{date_today}_learn_dl_cpds.log'

# Create logger
dlcpds_logger = logging.getLogger(__name__)
dlcpds_logger.setLevel(logging.DEBUG)  # Set the logger's level to DEBUG to capture all logs

# Create file handler for logging to a file
dlcpds_handler = logging.FileHandler(filename, mode='w')
dlcpds_handler.setLevel(logging.DEBUG)  # Set the handler's level

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
dlcpds_handler.setFormatter(formatter)

# Add the handler to the logger
dlcpds_logger.addHandler(dlcpds_handler)

dlcpds_logger.propagate = False  # Avoid passing logs up to the root logger


import warnings

# Suppress specific warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning, message='Probability values don\'t exactly sum to 1.')

# Suppress all warnings
warnings.filterwarnings('ignore')

#SET UP DEFAULT_DIR
DEFAULT_DIR = 'datasets/rmulaudzi/'
utility_function.ensure_directory_exists(DEFAULT_DIR)

# Normalize the input data using Min-Max scaling
def normalize_data_min_max(data):
    scaler = MinMaxScaler()
    normalized_data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
    return normalized_data

# Normalize the input data using Z-score normalization
def normalize_data_z_score(data):
    scaler = StandardScaler()
    normalized_data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
    return normalized_data

# Use macbook GPUs if available
def _use_gpus():
    # Check for GPU availability and configure TensorFlow accordingly
    gpus = tf.config.experimental.list_physical_devices('GPU')
    
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            dlcpds_logger.info(f"{len(gpus)}, 'Physical GPUs,', {len(logical_gpus)}, 'Logical GPUs'")

            return True
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            dlcpds_logger.error(f"Error in LearningDeepCPDs {e}")

            return False

def learn_cpd_for_node(node, data, true_model, learnt_bn_structure, num_parameters, indegree=2,
                       es_patience=1, train_size=0.8, val_size=0.05, epochs=10, batch_size=32, 
                       sample_size=1000, visualize_it=False, run_id=None, experiment_id=None,
                       network_type='naive', normalization='min-max', sampling_method='5', state_values=None):
    """
    Learn Conditional Probability Distributions (CPDs) using a deep learning model for a single node.
    
    Parameters:
    - node (str): The node for which to learn the CPD.
    - data (DataFrame): The dataset containing the samples.
    - true_model (BayesianNetwork): The true Bayesian network model used for comparison.
    - learnt_bn_structure (BayesianNetwork or dict): The learned Bayesian network structure.
    - num_parameters (int): Number of parameters for the deep learning model.
    - indegree (int): The maximum indegree of the Bayesian network.
    - es_patience (int): Patience for early stopping during model training.
    - train_size (float): The proportion of the dataset to include in the train split.
    - val_size (float): The proportion of the training dataset to include in the validation split.
    - epochs (int): The number of training epochs for the deep learning model.
    - batch_size (int): The batch size for training the deep learning model.
    - sample_size (int): The size of data to sample from the Bayesian network.
    - visualize_it (bool): Whether to visualize the model training process.
    - run_id, experiment_id: MLflow tracking parameters.
    - network_type (str): The type of deep learning network to use. Options include 'naive', 'simple', 'medium', 'large', 'bnn'.
    - sampling_method (str): The method to use for sampling the learned weights. Options include '1', '2', '3', '4'.
    - state_values (dict): The state values for the node.
    
    Accepted formats:
        * '1', '2', '3', '4'
        * Full method names ('weighted', 'stratified', 'kde', 'bayesian')
        * First letters ('w', 's', 'k', 'b')
    
    Returns:
    - A TabularCPD object for the node.
    """
    
    try: 
        #print(f"Processing node: {node}, Number of Parameters: {num_parameters}")
        # Configure logging
        dlcpds_logger = logging.getLogger(__name__)

        # Check for GPU availability and configure TensorFlow accordingly
        if _use_gpus():
            dlcpds_logger.debug("Using GPUs for deep learning model training.")

        dlcpds_logger.debug(f"Learning CPDs for node: {node}, with network type: {network_type}, and {num_parameters} parameters")

        # Ensure that the learned structure is a BayesianNetwork
        if isinstance(learnt_bn_structure, dict):
            learnt_bn_model = learnt_bn_structure['model']
        elif isinstance(learnt_bn_structure, BayesianNetwork):
            learnt_bn_model = learnt_bn_structure
        else:
            raise ValueError("learnt_bn_structure must be a BayesianNetwork or dict with key 'model'")

        # check that inputs are valid
        network_type = 'naive' if network_type not in ['naive', 'simple', 'medium', 'large', 'bnn', 'autoencoder'] else network_type
        sampling_method = '3' if sampling_method not in ['1', '2', '3', '4', 'weighted', 'stratified', 'kde', 'bayesian'] else sampling_method
        dlcpds_logger.debug(f"Network type: {network_type}, Sampling method: {sampling_method}")

        # Prepare output directory for artifacts
        #output_graph_dir = "outputs/graphs"
        output_graph_dir = os.path.join(DEFAULT_DIR, 'outputs', 'graphs')
        #os.makedirs(output_graph_dir, exist_ok=True)
        if not os.path.exists(output_graph_dir):
            os.makedirs(output_graph_dir, exist_ok=True)

        # Saving the entire array as an artifact
        #output_params_dir = "outputs/params"
        output_params_dir = os.path.join(DEFAULT_DIR, 'outputs', 'params')
        if not os.path.exists(output_params_dir):
            os.makedirs(output_params_dir, exist_ok=True)

        # Set up run name and configuration ID
        #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_id = f"{node}_cpd_{len(data.columns)}_nodes_{sample_size}_{network_type}"
        run_name = f"{config_id}_{network_type}_dnn_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Data and parameters preparation for the node
        # Factor group of the Bayesian network
        card = len(np.unique(data[node]))
        node_parents = true_model.get_parents(node)

        data = data.copy()
        data_index = node_parents + [node]
        data = data[data_index]

        # Normalize the data; does not impact performance but good practise
        if normalization == 'z-score':
            data = normalize_data_z_score(data)
        else:
            data = normalize_data_min_max(data)
        
        dlcpds_logger.debug(f"Data normalized for node {node} with parents {node_parents}")

        # Count NaN values in data
        nan_count = np.isnan(data).sum().sum()
        total_values = data.size  # Total number of values in the DataFrame

        dlcpds_logger.debug(f"Data for node {node} with parents {node_parents} and shape {data.shape}")
        dlcpds_logger.debug(f"Data shape: {data.shape}, Number of NaNs: {np.isnan(data).sum()}")
        dlcpds_logger.debug(f"Percentage of NaNs in data: {nan_count / total_values * 100:.2f}%")        
        
        # Check if the node represents a deterministic outcome (single parameter)
        if num_parameters == 1:
            #print(f"Node {node} identified as having a deterministic outcome.")
            
            # Handle deterministic outcome
            dlcpds_logger.info(f"Node {node} appears to have a deterministic outcome.")
            
            # Assuming binary outcome for simplicity; adjust based on your specific case
            outcome_value = data[node].unique()[0]
            cpd_values = [1.0] if outcome_value == 1 else [0.0, 1.0]
            
            # Create a TabularCPD for the deterministic outcome
            cpd = TabularCPD(variable=node, variable_card=2, values=[cpd_values],
                             evidence=None, evidence_card=None)
            
            dlcpds_logger.info(f"Created deterministic CPD for node {node}.")
            
            return cpd

        # Calculate parents_card here
        parents_card = [len(data[parent].unique()) for parent in node_parents if parent in data.columns]
        dlcpds_logger.debug(f"Parents cardinality for node {node}: {parents_card}")

        # Split data for training, validation, and testing
        train_data, validation_data, test_data = dl_model.split_data(data.values, train_size, val_size)
        dlcpds_logger.info("Data split for node %s with parents %s: Train - %d, Validation - %d, Test - %d", node, node_parents, len(train_data), len(validation_data), len(test_data))
        dlcpds_logger.debug(f"Number of NaNs in training data: {np.isnan(train_data).sum().sum()}")
        dlcpds_logger.debug(f"Number of NaNs in validation data: {np.isnan(validation_data).sum().sum()}")
        dlcpds_logger.debug(f"Number of NaNs in testing data: {np.isnan(test_data).sum().sum()}")
        
        # Remove NaN values from the data
        if np.isnan(train_data).any():
            train_data = train_data[~np.isnan(train_data).any(axis=1)]
        if np.isnan(test_data).any():
            test_data = test_data[~np.isnan(test_data).any(axis=1)]
        if np.isnan(validation_data).any():
            validation_data = validation_data[~np.isnan(validation_data).any(axis=1)]
        dlcpds_logger.debug("Testing data preped (nan removed) - %d, val - %d...", len(test_data), len(validation_data))

        # Prepare labels for the DL and split data
        # Model parameters only required for supervised learning
        # if no cpds are available, then we are in a unsupervised learning scenario
        if network_type == 'autoencoder':
            pass
        elif true_model.get_cpds():
            model_parameters, output_size = dl_model.prepare_parameters(node, data, true_model)
            train_parameters, validation_parameters, test_parameters = dl_model.split_data(model_parameters, train_size, val_size)

            # Ensure that the number of parameters matches the number of samples
            validation_parameters = validation_parameters[:len(validation_data)]
            test_parameters = test_parameters[:len(test_data)]

            dlcpds_logger.debug(f"Model parameters for node {node} with parents {node_parents} and shape {model_parameters.shape}")
            dlcpds_logger.debug(f"Model parameters shape: {model_parameters.shape}, Number of NaNs: {np.isnan(model_parameters).sum()}")
            dlcpds_logger.debug(f"Percentage of NaNs in model parameters: {np.isnan(model_parameters).sum() / model_parameters.size * 100:.2f}%")
        else:
            if network_type != 'autoencoder':
                dlcpds_logger.debug(f"Examples lables are required for supervised learning. Setting network_type: {network_type} to unsuperived defaul: autoencoder.")
                network_type = 'autoencoder'
            
            dlcpds_logger.debug(f"No CPDs available for node {node}. Proceeding with unsupervised learning.")

        # Ensure that the input shape matches the expected shape
        input_shape = train_data.shape[1]
        verbose = 2 if visualize_it else 0
        
        # Get the number of parameters for the node
        if true_model.get_cpds():
            node_cardinality = true_model.get_cardinality(node)
            
        else:
            node_cardinality = len(data[node].value_counts().index)
        
        parent_cardinality = 1

        if node_parents:
            for parent in node_parents:
                if true_model.get_cpds():
                    parent_cardinality += true_model.get_cardinality(parent)
                else:
                    parent_cardinality = len(data[parent].value_counts().index)

        num_parameters = node_cardinality * parent_cardinality

        # Model creation and training
        try:
            dlcpds_logger.info(f"Learning deep learning model for {node} with parents {node_parents} with {num_parameters}")
            if network_type == 'autoencoder':
                    autoencoder, encoder_model, es, latent_layer_name = dl_model.create_deep_learning_autoencoder_model(input_shape, num_parameters)
                    model = autoencoder
                    history = autoencoder.fit(train_data, train_data, epochs=epochs, batch_size=batch_size, validation_data=(validation_data, validation_data), callbacks=[es], verbose=1)
            else:
                model, es = dl_model.select_and_create_model(network_type, input_shape, output_size, num_parameters, indegree)
                history = dl_model.train_deep_learning_model(model, train_data, train_parameters, validation_data, validation_parameters, es, epochs, batch_size, verbose, run_id, run_name, config_id)

            dlcpds_logger.info(f"Learnt deep learning model trained for {node} with parents {node_parents}")
        except Exception as e:
            dlcpds_logger.error(f"Error in model training: {e}")
            raise ValueError(f"Deep Learning training to learn model. Model creation failed: {e}")

        # Model evaluation and processing
        try:
            if model is not None:
                if network_type == 'autoencoder':
                    # Get latent layer weights
                    evaluation_results = autoencoder.evaluate(test_data, test_data, batch_size=batch_size, verbose=verbose)
                    dlcpds_logger.debug(f"Autoencoder evaluation results: {evaluation_results}")
                else:
                    dl_model.evaluate_deep_learning_model(model, test_data, test_parameters, batch_size, verbose)
                dlcpds_logger.debug(f"Learning deep learning model evaluated for {node} with parents {node_parents}")
            else:
                dlcpds_logger.error(f"Model is None. Model training for {node} with parents {node_parents}")
                raise ValueError("Model is None. Model training")
        except Exception as e:
            dlcpds_logger.error(f"Error in model evaluation: {e}")
            raise ValueError(f"Deep Learning evaluation to learn model. Model creation failed: {e}")

        # Save and log model performance plot 
        if visualize_it:
            #performance_plot_filename = os.path.join(output_graph_dir, f"{run_name}_dl_performance.svg")
            dl_model.plot_model_performance(history)
            #dlcpds_logger.info(f"Model performance plot saved to {performance_plot_filename}")
        
        if network_type == 'autoencoder':
             dlcpds_logger.debug(f"Retrieving latent layer weights with encoder_model, latent_layer_name = {encoder_model}, {latent_layer_name} for node: {node} with parents: {node_parents}")
             learned_weights = dl_model.get_latent_layer_weights(encoder_model, latent_layer_name)
             learned_weights = np.array(learned_weights, dtype=float).flatten()
             dlcpds_logger.debug(f"Latent layer weights for node: {node} with parents: {node_parents}; retrieved weights: {learned_weights} with shape: {learned_weights.shape}")
        else:
            learned_weights = pre_process.flatten_weights(model)
            dlcpds_logger.debug(f"Flattened weights for node: {node} with parents: {node_parents}; retrieved weights: {learned_weights} with shape: {learned_weights.shape}")

        # Reshape weights to CPD and create TabularCPD
        dlcpds_logger.info(f"Reshaping weights to CPD for node: {node} with parents: {node_parents}; retrieved weights: {learned_weights} with shape: {learned_weights.shape} \n using sampling method: {sampling_method}")
        
        if node_parents:
            # Generate CPD using sampling method of choice: options 
            '''
            Accepted formats:
                * '1', '2', '3', '4'
                * Full method names ('weighted', 'stratified', 'kde', 'bayesian')
                * First letters ('w', 's', 'k', 'b')

            '''
            print(f"Sampling method: {sampling_method}")

            try:
                
                cpd_values = pre_process.execute_sampling_method(
                    learned_weights, card, parents_card, 
                    method=sampling_method
                )
                dlcpds_logger.debug(f"Generated CPD for node {node} with parents {node_parents}: {cpd_values}")
            except ValueError as e:
                dlcpds_logger.error(f"Error generating CPDs: {e}")
                raise ValueError(f"Error generating CPDs: {e}")
                
        else:
            #cpd_values, p_value, z_score = pre_process.reshape_weights_to_cpd(np.array(learned_weights, dtype=float), card, None)
            # Generate CPD using sampling method of choice: options 
            try:
                cpd_values = pre_process.execute_sampling_method(
                    learned_weights, card, None, 
                    method=sampling_method
                )
                dlcpds_logger.debug(f"Generated CPD for node {node} with parents {node_parents}: {cpd_values}")
            except ValueError as e:
                dlcpds_logger.error(f"Error generating CPDs: {e}")
                raise ValueError(f"Error generating CPDs: {e}")
        
        # Reverse order of CPD values
        #cpd_values = np.array(cpd_values)[::-1]

        #dlcpds_logger.debug(f'Learnt CPDs for node {node}: {cpd_values}, p-values: {p_value}, z-scores: {z_score}')
        dlcpds_logger.debug(f"Learnt CPDs for node {node}: {cpd_values}")

        # Create TabularCPD object for the node
        try:
            if state_values:
                state_names = {node: list(state_values)}
    
                for parent, parent_card in zip(node_parents, parents_card):
                    state_names[parent] = [f"state_{i}" for i in range(parent_card)]

                cpd = dl_model.create_tabular_cpd(node, card, np.array(cpd_values), node_parents, parents_card, state_names)
            else:
                cpd = dl_model.create_tabular_cpd(node, card, np.array(cpd_values), node_parents, parents_card)
            dlcpds_logger.debug(f"CPDs successfully created for node: {node} for run_name: {run_name}")
        except Exception as e:
            dlcpds_logger.error(f"Error for run_name: {run_name} in cpd creation: {e}")
            raise ValueError(f"CPD for run_name: {run_name} creation failed: {e}")

        # Clear TensorFlow session
        clear_session()  

        return cpd
        
    except Exception as e:
        dlcpds_logger.error(f"Exception in learn_cpd_for_node for node {node}: {e}", exc_info=True)
        # Return None or raise to indicate failure
        raise ValueError(f"Exception in learn_cpd_for_node for node {node}: {e}")