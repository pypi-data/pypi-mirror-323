#Suppressing the informational message
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

# Create a deep learning architecture to learn the parameters
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import keras
from keras import regularizers
from keras.callbacks import EarlyStopping
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, Conv1D, Flatten, LSTM, SimpleRNN, BatchNormalization, Reshape, Input
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Masking

# Create a MirroredStrategy.
strategy = tf.distribute.MirroredStrategy()

from . import Utils as utility_function

from datetime import datetime

import logging

# Configure logging
date_today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_directory = 'outputs/logs/'
utility_function.ensure_directory_exists(log_directory)  # Ensure the log directory exists
filename = f'{log_directory}{date_today}_create_dl_cpds.log'

# Create logger
dlcpds_logger = logging.getLogger(__name__)
dlcpds_logger.setLevel(logging.ERROR)  # Set the logger's level

# Create file handler for logging to a file
dlcpds_handler = logging.FileHandler(filename)
dlcpds_handler.setLevel(logging.ERROR)  # Set the handler's level

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
dlcpds_handler.setFormatter(formatter)

# Add the handler to the logger
dlcpds_logger.addHandler(dlcpds_handler)

def prepare_parameters(node, data, true_model):
    """ Prepare parameters for training the deep learning model. """
    cpd = true_model.get_cpds(node)
    
    if cpd is None:
        raise ValueError(f"No CPD found for node {node}")
    
    model_parameters = np.array(cpd.values).ravel()
    output_size = len(model_parameters)
    model_parameters = np.repeat(model_parameters, len(data), axis=0)[:len(data)]
    return to_categorical(model_parameters, num_classes=output_size), output_size

def split_data(data, train_size=0.8, val_size=0.05):
    """ Split data into training, validation, and testing sets. """
    train_data, test_data = train_test_split(data, train_size=train_size, test_size=1-train_size)
    train_data, validation_data = train_test_split(train_data, train_size=1-val_size, test_size=val_size)
    return train_data, validation_data, test_data

#from keras.losses import kullback_leibler_divergence
from tensorflow.keras.losses import kullback_leibler_divergence
from tensorflow.keras.losses import KLDivergence

def select_and_create_model(network_type, input_shape, output_size, num_parameters, indegree, es_patience=1):
    """
    Select and create a deep learning model based on the specified network type.

    Parameters:
    - network_type (str): Type of the deep learning network ('naive', 'simple', 'medium', 'large', etc.).
    - input_shape (int): The shape of the input data.
    - output_size (int): The size of the output layer.
    - num_parameters (int): Number of parameters for the deep learning model.
    - indegree (int): The maximum indegree of the Bayesian network.
    - es_patience (int): Patience parameter for early stopping.

    Returns:
    - model: The created deep learning model.
    - es: The early stopping callback.
    """
    #print('Number of devices: {}'.format(strategy.num_replicas_in_sync))
    # Open a strategy scope.
    #with strategy.scope():
    dlcpds_logger.debug(f"Learning {network_type} DL weights for {num_parameters} paramaters")
    
    if network_type == 'naive':
        model, es = create_deep_learning_naive_model(input_shape, output_size, num_parameters, es_patience, network_type)
    elif network_type == 'simple':
        model, es = create_deep_learning_simple_model(input_shape, output_size, num_parameters, es_patience, network_type)
    elif network_type == 'medium':
        model, es = create_deep_learning_medium_model(input_shape, output_size, num_parameters, indegree, es_patience, network_type)
    elif network_type == 'large':
        model, es = create_deep_learning_large_model(input_shape, output_size, num_parameters, indegree, es_patience, network_type)
    elif network_type == 'cnn':
        model, es = create_deep_learning_cnn_model(input_shape, output_size, es_patience, network_type)
    elif network_type == 'lstm':
        model, es = create_deep_learning_lstm_model(input_shape, output_size, es_patience, network_type)
    else:
        model, es = create_deep_learning_model(input_shape, output_size, num_parameters, indegree, es_patience, network_type)
    
    dlcpds_logger.debug(f"Learnt {network_type} DL weights for {num_parameters} paramaters")
    
    return model, es


def create_deep_learning_model(input_size, output_size, es_patience=2, network_type = 'general_network'):
    """
    Create a deep learning model architecture for parameter learning.

    Parameters:
    - input_size (int): The size of the input layer.
    - output_size (int): The size of the output layer.

    Returns:
    - model (keras.Model): The created deep learning model.
    - es (keras.callbacks.EarlyStopping): Early stopping callback to prevent overfitting.
    """
    if not isinstance(input_size, int) or not isinstance(output_size, int):
        dlcpds_logger.error("Input and output sizes must be integers for learning DL")
        raise ValueError("Input and output sizes must be integers")
    
    unique_str = np.random.randint(10000, 99999)  # Generate a unique identifier
    
    with strategy.scope():
        model = keras.Sequential(name=f"{network_type}_{unique_str}")
        model.add(keras.layers.Dense(units=output_size, activation='relu', input_shape=(input_size,), name=f"{network_type}_{unique_str}_l1"))
        model.add(keras.layers.Dense(units=512, kernel_regularizer=regularizers.l2(0.0001), activation='relu', name=f"{network_type}_{unique_str}_l2"))
        model.add(keras.layers.Dropout(0.5, name=f"{network_type}_{unique_str}_l3"))  # Corrected
        model.add(keras.layers.Dense(units=256, kernel_regularizer=regularizers.l2(0.0001), activation='relu', name=f"{network_type}_{unique_str}_l4"))  # Corrected
        model.add(keras.layers.Dropout(0.5, name=f"{network_type}_{unique_str}_l5"))  # Corrected
        model.add(keras.layers.Dense(units=128, kernel_regularizer=regularizers.l2(0.0001), activation='relu', name=f"{network_type}_{unique_str}_l6"))  # Corrected
        model.add(keras.layers.Dropout(0.5, name=f"{network_type}_{unique_str}_l7"))  # Corrected
        model.add(keras.layers.Dense(units=output_size, activation='softmax', name=f"{network_type}_{unique_str}_l8"))  # Corrected
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])
        
        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} paramaters")
        
    return model, es

def create_deep_learning_naive_model(input_shape, output_size, num_parameters, es_patience=2, network_type= 'naive_network'):
    """
    Create a simple MLP where the number of weights equals the number of parameters in a Bayesian Network.
    """
    unique_str = np.random.randint(10000, 99999) 
    
    with strategy.scope():
        model = Sequential(name=f"{network_type}_{unique_str}_l1")
        model.add(Dense(units=output_size, activation='relu', input_shape=(input_shape,), name=f"{network_type}_{unique_str}_l2"))    
        model.add(Masking(mask_value=np.nan, name=f"{network_type}_{unique_str}_masking"))
        model.add(Dense(units=num_parameters, activation='relu', name=f"{network_type}_{unique_str}_l3"))
        model.add(Dense(units=output_size, activation='softmax', name=f"{network_type}_{unique_str}_l4"))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} paramaters")
    
    return model, es 

def create_deep_learning_simple_model(input_shape, output_size, num_parameters, es_patience=2, network_type= 'simple_network'):
    """
    Create an MLP where the number of weights is 2-5x number of parameters.
    """
    unique_str = np.random.randint(10000, 99999) 
    
    with strategy.scope():
        factor = np.random.randint(2, 6)
        model = Sequential(name=f"{network_type}_{unique_str}_l1")
        model.add(Dense(units=output_size, activation='relu', input_shape=(input_shape,), name=f"{network_type}_{unique_str}_l2"))
        model.add(Masking(mask_value=np.nan, name=f"{network_type}_{unique_str}_masking"))
        model.add(Dense(units=factor * num_parameters, activation='relu', name=f"{network_type}_{unique_str}_l3"))
        model.add(Dense(units=output_size, activation='softmax', name=f"{network_type}_{unique_str}_l4"))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} paramaters")

    return model, es 

def create_deep_learning_medium_model(input_shape, output_size, num_parameters, indegree, es_patience=2, network_type= 'medium_network'):
    """
    Create an MLP with 5-10x number of parameters, number of layers should be indegree.
    """
    unique_str = np.random.randint(10000, 99999) 
    indegree = 2
    
    with strategy.scope():
        factor = np.random.randint(5, 11)
        model = Sequential(name=f"{network_type}_{unique_str}_l1")
        model.add(Dense(units=output_size, activation='relu', input_shape=(input_shape,), name=f"{network_type}_{unique_str}_l2"))
        model.add(Masking(mask_value=np.nan, name=f"{network_type}_{unique_str}_masking"))
        for i in range(indegree):
            model.add(Dense(units=factor * num_parameters, activation='relu', name=f"{network_type}_{i}_{unique_str}_l3"))
            model.add(Dropout(0.5))
        model.add(Dense(units=output_size, activation='softmax', name=f"{network_type}_{unique_str}_l4"))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} paramaters")

    return model, es 

def create_deep_learning_large_model(input_shape, output_size, num_parameters, indegree, es_patience=2, network_type= 'large_network'):
    """
    Create an MLP with 10-20x number of parameters, number of layers should be indegree.
    """
    unique_str = np.random.randint(10000, 99999) 
    indegree = 3
    
    with strategy.scope():
        factor = np.random.randint(10, 20)  
        model = Sequential(name=f"{network_type}_{unique_str}_l1")
        model.add(Dense(units=output_size, activation='relu', input_shape=(input_shape,), name=f"{network_type}_{unique_str}_l2"))
        model.add(Masking(mask_value=np.nan, name=f"{network_type}_{unique_str}_masking"))
        for i in range(indegree):
            model.add(Dense(units=factor * num_parameters, activation='relu', name=f"{network_type}_{i}_{unique_str}_l3"))
            model.add(Dropout(0.5))
        model.add(Dense(units=output_size, activation='softmax', name=f"{network_type}_{unique_str}_l3"))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} paramaters")

    return model, es 

def create_deep_learning_cnn_model(input_shape, output_size, es_patience=2, network_type='cnn_network'):
    """
    Adapted CNN model for tabular data.
    """
    unique_str = np.random.randint(10000, 99999)
    
    with strategy.scope():
        model = Sequential(name=f"{network_type}_{unique_str}")
        # Reshape input to have 1 channel
        model.add(Reshape((input_shape, 1), input_shape=(input_shape,), name=f"{network_type}_{unique_str}_reshape"))
        model.add(Masking(mask_value=np.nan, name=f"{network_type}_{unique_str}_masking"))

        # Use 1D convolutions for tabular data
        model.add(Conv1D(16, kernel_size=3, activation='relu', padding='same', name=f"{network_type}_{unique_str}_conv1"))
        model.add(Conv1D(64, 3, activation='relu', padding='same', name=f"{network_type}_{unique_str}_conv2"))
        model.add(Flatten(name=f"{network_type}_{unique_str}_flatten"))
        model.add(Dense(32, activation='relu', name=f"{network_type}_{unique_str}_dense1"))
        model.add(Dropout(0.5, name=f"{network_type}_{unique_str}_dropout"))
        model.add(Dense(output_size, activation='softmax', name=f"{network_type}_{unique_str}_output"))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
    return model, es
 
'''
def create_deep_learning_lstm_model(input_shape, output_size, es_patience=2, network_type='lstm_network'):
    """
    Adapted LSTM model for tabular data, treating each feature as a separate timestep.
    Parameters:
    - input_shape (int): Number of features, treated as timesteps in the model.
    - output_size (int): The size of the output layer, typically the number of classes for classification.
    - es_patience (int): Early stopping patience.
    - network_type (str): A label for the network type.
    Returns:
    - model (Sequential): The compiled Keras model.
    - es (EarlyStopping): The early stopping callback.
    """
    unique_str = np.random.randint(10000, 99999)
    
    with strategy.scope():
        model = Sequential(name=f"{network_type}_{unique_str}")
        # Reshape input to add a 'timesteps' dimension
        model.add(Reshape((input_shape, 1), input_shape=(input_shape,), name=f"{network_type}_{unique_str}_reshape"))
        # First LSTM layer, assuming each feature is a separate timestep
        model.add(LSTM(32, return_sequences=True, name=f"{network_type}_{unique_str}_lstm1"))
        # Second LSTM layer
        model.add(LSTM(32, name=f"{network_type}_{unique_str}_lstm2"))
        model.add(Dropout(0.5, name=f"{network_type}_{unique_str}_dropout"))
        model.add(Dense(output_size, activation='softmax', name=f"{network_type}_{unique_str}_output"))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} parameters")

    return model, es
'''

def create_deep_learning_lstm_model(input_shape, output_size, es_patience=2, network_type='lstm_network'):
    """
    Adapted LSTM model for tabular data, treating each feature as a separate timestep.
    Parameters:
    - input_shape (int): Number of features, treated as timesteps in the model.
    - output_size (int): The size of the output layer, typically the number of classes for classification.
    - es_patience (int): Early stopping patience.
    - network_type (str): A label for the network type.
    Returns:
    - model (Sequential): The compiled Keras model.
    - es (EarlyStopping): The early stopping callback.
    """
    unique_str = np.random.randint(10000, 99999)
    
    with strategy.scope():
        model = Sequential(name=f"{network_type}_{unique_str}")
        # Reshape input to add a 'timesteps' dimension
        model.add(Reshape((input_shape, 1), input_shape=(input_shape,), name=f"{network_type}_{unique_str}_reshape"))
        # Masking layer to ignore NaN values
        model.add(Masking(mask_value=np.nan, name=f"{network_type}_{unique_str}_masking"))
        # First LSTM layer, assuming each feature is a separate timestep
        model.add(LSTM(32, return_sequences=True, name=f"{network_type}_{unique_str}_lstm1"))
        # Second LSTM layer
        model.add(LSTM(32, name=f"{network_type}_{unique_str}_lstm2"))
        model.add(Dropout(0.5, name=f"{network_type}_{unique_str}_dropout"))
        model.add(Dense(output_size, activation='softmax', name=f"{network_type}_{unique_str}_output"))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} parameters")

    return model, es

# Create and configure the autoencoder model with dropout layers
from tensorflow.keras.models import Model

def create_deep_learning_autoencoder_model(input_shape, num_parameters, es_patience=2, dropout_rate=0.2, network_type='autoencoder_network'):
    unique_str = np.random.randint(10000, 99999)
    latent_layer_name = f"{network_type}_{unique_str}_latent_space"
    
    input_layer = Input(shape=(input_shape,), name=f"{network_type}_{unique_str}_input")
        
    # Encoder
    encoder = Dense(units=128, activation='relu', name=f"{network_type}_{unique_str}_encoder_l1")(input_layer)
    encoder = Dropout(rate=dropout_rate, name=f"{network_type}_{unique_str}_dropout_l1")(encoder)
    encoder = Dense(units=64, activation='relu', name=f"{network_type}_{unique_str}_encoder_l2")(encoder)
    encoder = Dropout(rate=dropout_rate, name=f"{network_type}_{unique_str}_dropout_l2")(encoder)
    latent_space = Dense(units=num_parameters, activation='relu', name=latent_layer_name)(encoder)
    
    # Decoder
    decoder = Dense(units=64, activation='relu', name=f"{network_type}_{unique_str}_decoder_l1")(latent_space)
    decoder = Dropout(rate=dropout_rate, name=f"{network_type}_{unique_str}_dropout_l3")(decoder)
    decoder = Dense(units=128, activation='relu', name=f"{network_type}_{unique_str}_decoder_l2")(decoder)
    decoder = Dropout(rate=dropout_rate, name=f"{network_type}_{unique_str}_dropout_l4")(decoder)
    output_layer = Dense(units=input_shape, activation='sigmoid', name=f"{network_type}_{unique_str}_output")(decoder)
    
    autoencoder = Model(inputs=input_layer, outputs=output_layer, name=f"{network_type}_{unique_str}")
    encoder_model = Model(inputs=input_layer, outputs=latent_space, name=f"{network_type}_{unique_str}_encoder")
    
    autoencoder.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.metrics.KLDivergence()])

    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)

    return autoencoder, encoder_model, es, latent_layer_name


import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Lambda, Dropout, Layer
from tensorflow.keras.models import Model
from tensorflow.keras.losses import binary_crossentropy
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

# Sampling layer for the VAE
class Sampling(Layer):
    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

# Custom loss layer to calculate VAE loss
class VAE_Loss_Layer(Layer):
    def call(self, inputs):
        x, x_decoded, z_mean, z_log_var = inputs
        reconstruction_loss = binary_crossentropy(x, x_decoded)
        reconstruction_loss *= x.shape[1]
        kl_loss = 1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
        kl_loss = tf.reduce_sum(kl_loss, axis=-1)
        kl_loss *= -0.5
        total_loss = tf.reduce_mean(reconstruction_loss + kl_loss)
        self.add_loss(total_loss)
        return x_decoded

# VAE model creation function
def create_variational_autoencoder_model(input_shape, num_parameters, es_patience=5, dropout_rate=0.2, network_type='vae_normal_network'):
    inputs = Input(shape=(input_shape,), name='encoder_input')
    unique_str = np.random.randint(10000, 99999)
    latent_layer_name = f"{network_type}_{unique_str}_latent_space"
    
    # Encoder
    x = Dense(128, activation='relu')(inputs)
    x = Dropout(rate=dropout_rate)(x)
    x = Dense(64, activation='relu')(x)
    x = Dropout(rate=dropout_rate)(x)
    
    # Latent Variables
    z_mean = Dense(num_parameters, name='z_mean')(x)
    z_log_var = Dense(num_parameters, name='z_log_var')(x)
    
    z = Sampling(name=latent_layer_name)([z_mean, z_log_var])
    
    # Decoder
    decoder_input = Dense(64, activation='relu')(z)
    decoder_input = Dropout(rate=dropout_rate)(decoder_input)
    decoder_input = Dense(128, activation='relu')(decoder_input)
    decoder_input = Dropout(rate=dropout_rate)(decoder_input)
    outputs = Dense(input_shape, activation='sigmoid')(decoder_input)
    
    # Apply the VAE loss as a custom layer
    outputs_with_loss = VAE_Loss_Layer()([inputs, outputs, z_mean, z_log_var])
    
    vae = Model(inputs, outputs_with_loss, name='vae')
    
    # Compile the model
    vae.compile(optimizer='adam')
    
    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
    
    return vae, es, z_mean, z_log_var

def get_latent_parameters(model, latent_layer_name=['z_mean', 'z_log_var']):
    z_mean_model = Model(inputs=model.input, outputs=model.get_layer(latent_layer_name[0]).output)
    z_log_var_model = Model(inputs=model.input, outputs=model.get_layer(latent_layer_name[1]).output)

    return z_mean_model, z_log_var_model

def get_latent_layer_weights(model, latent_layer_name):
    latent_layer = model.get_layer(latent_layer_name)
    weights = latent_layer.get_weights()[0]
    # Apply softmax and reshape weights to (parameters, 1)
    softmax_weights = tf.nn.softmax(weights, axis=0).numpy()
    reshaped_weights = np.mean(softmax_weights, axis=0).reshape(-1, 1)
    return reshaped_weights

import tensorflow as tf
import tensorflow_probability as tfp

def prior(kernel_size, bias_size, dtype=None):
    n = kernel_size + bias_size
    prior_model = Sequential([
        tfp.layers.DistributionLambda(lambda t: tfp.distributions.MultivariateNormalDiag(
            loc=tf.zeros(n), scale_diag=tf.ones(n)))
    ])
    
    return prior_model

def posterior(kernel_size, bias_size, dtype=None):
    n = kernel_size + bias_size
    posterior_model = Sequential([
        tfp.layers.VariableLayer(tfp.layers.MultivariateNormalTriL.params_size(n), dtype=dtype),
        tfp.layers.MultivariateNormalTriL(n)
    ])
    return posterior_model

def create_deep_learning_bnn_model(input_shape, output_size, num_parameters, indegree, es_patience=2, network_type= 'bnn_network'):
    """
    Create a Bayesian Neural Network model.
    """
    unique_str = np.random.randint(10000, 99999) 
    
    with strategy.scope():
        model = Sequential(name=f"{network_type}_{unique_str}")
        for _ in range(indegree - 1):
            model.add(tfp.layers.DenseVariational(units=num_parameters, input_shape=input_shape,
                                                  make_prior_fn=prior, make_posterior_fn=posterior,
                                                  kl_weight=1/input_shape[0], activation='relu'))
            model.add(Dropout(0.5))
        model.add(tfp.layers.DenseVariational(units=output_size,
                                              make_prior_fn=prior, make_posterior_fn=posterior,
                                              kl_weight=1/input_shape[0], activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', tf.keras.losses.KLDivergence()])

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=es_patience)
        
        dlcpds_logger.debug(f"Learnt {network_type} DL model with {model.count_params()} paramaters")

    return model, es 


def train_deep_learning_model(model, train_data, train_parameters, 
                              validation_data, validation_parameters, 
                              es, epochs = 10, batch_size = 32, verbose = 1, run_id=None, run_name=None, config_id=None):
    """
    Train the deep learning model on the provided data.

    Parameters:
    - model (keras.Model): The deep learning model.
    - train_data (numpy.array): Training data.
    - train_parameters (numpy.array): Training parameters.
    - validation_data (numpy.array): Validation data.
    - validation_parameters (numpy.array): Validation parameters.
    - es (keras.callbacks.EarlyStopping): Early stopping callback.

    Returns:
    - history (keras.callbacks.History): Training history object.
    """
    if not isinstance(model, keras.Model):
        dlcpds_logger.error("Model must be a Keras model instance")
        raise ValueError("Model must be a Keras model instance")
    
    with strategy.scope():    
        history = model.fit(
            train_data, train_parameters, 
            epochs=epochs, 
            batch_size=batch_size, 
            validation_data=(validation_data, validation_parameters), 
            callbacks=[es], 
            verbose=verbose
        )
    
    dlcpds_logger.debug(f"Trained DL for {run_name}")
    
    return history

def evaluate_deep_learning_model(model, test_data, test_parameters, batch_size=32, verbose = 1):
    """
    Evaluate the performance of the deep learning model.

    Parameters:
    - model (keras.Model): The deep learning model.
    - test_data (numpy.array): Test data.
    - test_parameters (numpy.array): Test parameters.
    """
    if not isinstance(model, keras.Model):
        dlcpds_logger.error("Model must be a Keras model instance")
        raise ValueError("Model must be a Keras model instance")
        
    with strategy.scope():
        model.evaluate(test_data, test_parameters, batch_size=batch_size, verbose = verbose)
        
    dlcpds_logger.debug(f"Evluated DL model")

def plot_model_performance(history, filename=None):
    """
    Plot the performance of the deep learning model.

    Parameters:
    - history (keras.callbacks.History): Training history object.
    """
    if not isinstance(history, tf.keras.callbacks.History):
        raise ValueError("History must be a Keras History object")

    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
       
    '''
    if bool(filename):
        plt.savefig(filename)
        plt.close()
    '''
    plt.show()

import networkx as nx
import matplotlib.pyplot as plt
from pgmpy.models import BayesianNetwork

def visualize_bayesian_network(model, bn_visualization_filename=None):
    """
    Visualize the Bayesian network with nodes and directed edges.
    
    Parameters:
    - model (BayesianNetwork): The Bayesian network model from pgmpy.
    - bn_visualization_filename (str): Filename where the visualization will be saved.
    """
    if not isinstance(model, BayesianNetwork):
        raise ValueError("Model must be a BayesianNetwork object from pgmpy")
    
    cpds = model.cpds
    
    if not bool(cpds):
        raise ValueError("Model must be a BayesianNetwork with valid CPDs")
    
    # Initialize a directed graph
    graph = nx.DiGraph()
    
    # Add nodes and edges to the graph
    for cpd in cpds:
        graph.add_node(cpd.variable)
        for evidence in cpd.variables[1:]:  # Skipping the first variable which is the node itself
            graph.add_edge(evidence, cpd.variable)
        #if bool(model.get_parents(str(cpd.variable))):
        #    print(f"\nP{cpd.variable} | {str(model.get_parents((cpd.variable)))} CPDs\n",cpd)
        #else:
        #    print(f"\nP{cpd.variable} CPDs\n",cpd)

    # Generate positions for each node for consistent graphs
    pos = nx.layout.circular_layout(graph)

    # Draw the graph
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=16, arrowsize=20)
    
    # Draw edge labels (conditional dependencies)
    edge_labels = {(parent, child): f"P({child}|{parent})" for parent, child in graph.edges}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=12, label_pos=0.5)

    # Save the plot to the specified file
    '''
    if bool(bn_visualization_filename):
        plt.savefig(bn_visualization_filename)
        plt.close()
    '''
    
    plt.show()



def generate_cpd_values(num_categories, num_parents):
    """
    Generate random values for a Conditional Probability Distribution (CPD).

    Parameters:
    - num_categories (int): The number of categories (states) the node can take.
    - num_parents (int): The number of parents the node has.

    Returns:
    - cpd_values (numpy.array): Randomly generated CPD values.
    """
    if not (isinstance(num_categories, int) and isinstance(num_parents, int)):
        raise ValueError("Number of categories and parents must be integers")

    num_values = num_categories ** (num_parents + 1)
    cpd_values = np.random.rand(num_values)
    cpd_values = cpd_values.reshape((num_categories, -1))
    cpd_values = cpd_values / np.sum(cpd_values, axis=1, keepdims=True)

    return cpd_values

from pgmpy.factors.discrete import TabularCPD

def create_tabular_cpd(node, card, cpd_values, parents, parents_card):
    """
    Create a TabularCPD instance for a given node in the Bayesian network.

    Parameters:
    - node (str): The node for which the CPD is being created.
    - cpd_values (np.array): The values of the CPD.
    - parents (list): List of parent nodes.
    - parents_card (list): Cardinalities of the parent nodes.

    Returns:
    - TabularCPD: An instance of TabularCPD for the given node.
    """
    if parents:
        # If the node has parents, we use them in the CPD
        cpd = TabularCPD(variable=node, variable_card=card,
                         values=cpd_values, evidence=parents,
                         evidence_card=parents_card)
    else:
        # If the node has no parents
        cpd = TabularCPD(variable=node, variable_card=card,
                         values=cpd_values)

    return cpd

def calculate_cpd_parameters(card, num_parents):
    """
    Calculate the number of parameters for a CPD.

    Parameters:
    - card (int): Cardinality of the node, i.e., the number of categories (states) it can take.
    - num_parents (int): Number of parents the node has in the Bayesian network.

    Returns:
    - num_params (int): Total number of parameters in the CPD.
    """
    if not (isinstance(card, int) and isinstance(num_parents, int)):
        raise ValueError("Cardinality and number of parents must be integers")

    num_params = card ** (num_parents + 1)
    return num_params

def generate_shape(num_parents, card):
    """
    Generate the shape of a CPD array.

    Parameters:
    - num_parents (int): Number of parents of a node.
    - card (int): Cardinality of the node.

    Returns:
    - shape (tuple): The shape of the CPD array.
    """
    if not (isinstance(num_parents, int) and isinstance(card, int)):
        raise ValueError("Number of parents and cardinality must be integers")

    return (card, card ** num_parents)