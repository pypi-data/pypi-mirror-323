import numpy as np
from scipy.stats import norm
from scipy.stats import zscore
from scipy.special import softmax

def normalize_and_reshape(weights, variable_card, parents_card, tolerance=0.5, n_times=100):
    """
    Normalize and reshape a flat array of weights into a conditional probability distribution (CPD)
    by repeated random sampling and averaging.
    This is not the prefered method because it is difficult to get a sample mean close to the population mean due to the sampling     appraoch.
    The alternative function is reshape_weights_to_cpd(weights, variable_card, parents_card) which is the prefered appraoch.

    Parameters:
    - weights (numpy.ndarray): A flat array of weights.
    - variable_card (int): Cardinality (number of states) of the variable.
    - parents_card (list): List of cardinalities of the variable's parents.
    - tolerance (float): Tolerance for the mean comparison.
    - n_times (int): Number of times to repeat the sampling process.

    Returns:
    - numpy.ndarray: A normalized CPD array.
    """
    if not isinstance(weights, np.ndarray) or weights.ndim != 1:
        raise ValueError("Weights must be a 1-dimensional numpy array.")
    if not isinstance(variable_card, int) or variable_card <= 0:
        raise ValueError("Variable card must be a positive integer.")
    if not isinstance(parents_card, list) or not all(isinstance(c, int) and c > 0 for c in parents_card):
        raise ValueError("Parents card must be a list of positive integers.")
    if not isinstance(tolerance, float) or not 0 <= tolerance <= 1:
        raise ValueError("Tolerance must be a float between 0 and 1.")
    if not isinstance(n_times, int) or n_times <= 0:
        raise ValueError("N_times must be a positive integer.")

    total_parent_states = np.prod(parents_card) if parents_card else 1
    desired_shape = (variable_card, total_parent_states)

    reshaped_weights_array = np.zeros((n_times,) + desired_shape)
    for i in range(n_times):
        random_indices = np.random.choice(weights.size, size=desired_shape, replace=False)
        reshaped_weights = weights[random_indices].reshape(desired_shape)
        reshaped_weights /= reshaped_weights.sum(axis=0, keepdims=True)
        reshaped_weights_array[i] = reshaped_weights

    mean_weights = np.mean(reshaped_weights_array, axis=0)
    mean_of_means = np.mean(mean_weights)

    if np.abs(mean_of_means - np.mean(weights)) / np.mean(weights) > tolerance:
        raise ValueError("The mean of the reshaped weights is outside the tolerance range.")

    return mean_weights

import numpy as np
from scipy.stats import gaussian_kde, dirichlet

def weighted_sampling_cpd(weights, variable_card, parents_card):
    """
    Perform weighted sampling based on the probability distribution of the weights.
    Arguments:
    - weights: Array of weight values (treated as probabilities).
    - variable_card: Cardinality of the variable to which the CPD corresponds.
    - parents_card: Cardinalities of the parent variables.
    
    Returns:
    - A conditional probability distribution matrix.
    """
    total_parent_states = np.prod(parents_card) if parents_card else 1
    desired_shape = (variable_card, total_parent_states)
    weights_normalized = weights / np.sum(weights)
    sample_indices = np.random.choice(
        len(weights), size=np.prod(desired_shape), p=weights_normalized, replace=True
    )
    sampled_weights = weights[sample_indices].reshape(desired_shape)
    cpd = sampled_weights / sampled_weights.sum(axis=0, keepdims=True)
    return cpd

def stratified_sampling_cpd(weights, variable_card, parents_card, num_bins=4):
    """
    Perform stratified sampling by dividing weights into strata (bins) and calculate CPD using the mean of each stratum.
    
    Arguments:
    - weights: Array of weight values.
    - variable_card: Cardinality of the variable to which the CPD corresponds.
    - parents_card: Cardinalities of the parent variables.
    - num_bins: Number of bins to divide the weight space into.
    
    Returns:
    - A conditional probability distribution matrix.
    """
    # Calculate the total number of parent states
    total_parent_states = np.prod(parents_card) if parents_card else 1
    desired_shape = (variable_card, total_parent_states)

    # Define bins for stratification
    bins = np.linspace(min(weights), max(weights), num=num_bins + 1)
    strata_indices = np.digitize(weights, bins) - 1

    # Calculate the mean weight in each stratum
    stratified_means = []
    for i in range(num_bins):
        stratum_weights = weights[strata_indices == i]
        if len(stratum_weights) > 0:
            stratified_means.append(np.mean(stratum_weights))
    
    # Expand to match the required CPD size by repeating or interpolating means
    expanded_means = np.resize(stratified_means, np.prod(desired_shape))

    # Reshape to form the conditional probability distribution matrix
    cpd = expanded_means.reshape(desired_shape)

    # Normalize columns to ensure probabilities sum to 1
    cpd /= cpd.sum(axis=0, keepdims=True)
    
    return cpd

def kde_based_sampling_cpd(weights, variable_card, parents_card, bandwidth=0.2):
    """
    Perform sampling using a kernel density estimate (KDE) of the weights.
    Arguments:
    - weights: Array of weight values.
    - variable_card: Cardinality of the variable to which the CPD corresponds.
    - parents_card: Cardinalities of the parent variables.
    - bandwidth: Bandwidth parameter for the KDE (affects smoothness).
    
    Returns:
    - A conditional probability distribution matrix.
    """
    total_parent_states = np.prod(parents_card) if parents_card else 1
    desired_shape = (variable_card, total_parent_states)
    kde = gaussian_kde(weights, bw_method=bandwidth)
    sampled_weights = kde.resample(size=np.prod(desired_shape)).flatten()
    sampled_weights = np.abs(sampled_weights)  # Ensure non-negative
    cpd = sampled_weights.reshape(desired_shape)
    cpd /= cpd.sum(axis=0, keepdims=True)
    return cpd

def bayesian_dirichlet_cpd(weights, variable_card, parents_card, prior=0.5):
    """
    Perform Bayesian sampling using a Dirichlet distribution.
    Arguments:
    - weights: Array of weight values.
    - variable_card: Cardinality of the variable to which the CPD corresponds.
    - parents_card: Cardinalities of the parent variables.
    - prior: Scalar to adjust the prior counts (higher values enforce stronger priors).
    
    Returns:
    - A conditional probability distribution matrix.
    """
    total_parent_states = np.prod(parents_card) if parents_card else 1
    desired_shape = (variable_card, total_parent_states)
    
    # Calculate the mean of weights and replicate it for all required entries
    mean_weight = np.mean(weights)
    alpha = np.full(np.prod(desired_shape), mean_weight * prior + 1e-5)
    
    # Sample the Dirichlet distribution for each parent state
    sampled_weights = np.zeros(desired_shape)
    for i in range(total_parent_states):
        # Use a slice of alpha corresponding to the variable's cardinality
        alpha_slice = alpha[i * variable_card:(i + 1) * variable_card]
        sampled_weights[:, i] = dirichlet(alpha_slice).rvs()

    # Normalize columns to ensure probabilities sum to 1
    sampled_weights /= sampled_weights.sum(axis=0, keepdims=True)

    return sampled_weights

def execute_sampling_method(weights, variable_card, parents_card, method, **kwargs):
    """
    Executes the specified sampling method based on user input with error handling.
    Arguments:
    - weights: Array of weight values.
    - variable_card: Cardinality of the variable to which the CPD corresponds.
    - parents_card: Cardinalities of the parent variables.
    - method: Identifier for the sampling method. Accepted formats:
        * '1', '2', '3', '4'
        * Full method names ('weighted', 'stratified', 'kde', 'bayesian')
        * First letters ('w', 's', 'k', 'b')
    - kwargs: Additional parameters for specific methods (optional).
    
    Returns:
    - A conditional probability distribution matrix or an error message.
    """
    method_mapping = {
        "1": "weighted",
        "2": "stratified",
        "3": "kde",
        "4": "bayesian",
        "5": "normalize_and_reshape",
        "w": "weighted",
        "s": "stratified",
        "k": "kde",
        "b": "bayesian",
        "n": "normalize_and_reshape",
        "normal": "normalize_and_reshape",
        "weighted": "weighted",
        "stratified": "stratified",
        "kde": "kde",
        "bayesian": "bayesian",
    }

    if isinstance(method, str):
        method = method.lower().strip()
    
    if isinstance(method, int):
        method_key = str(method)
    
    method_key = method_mapping.get(method)
    
    # Ensure non-negative weights
    weights = np.abs(weights)

    if not method_key:
        method_key = "stratified"  # Default to stratified sampling
        print(
            f"Invalid method '{method}'. Defaulting to 'stratified' (method '2'). Choose from: "
            f"1, 2, 3, 4, 'weighted', 'stratified', 'kde', or 'bayesian'."
        )

    
    sampling_methods = {
        "weighted": weighted_sampling_cpd,
        "stratified": stratified_sampling_cpd,
        "kde": kde_based_sampling_cpd,
        "bayesian": bayesian_dirichlet_cpd,
        "normalize_and_reshape": normalize_and_reshape
    }
    
    selected_method = sampling_methods[method_key]
    try:
        return selected_method(weights, variable_card, parents_card, **kwargs)
    except TypeError as e:
        raise ValueError(
            f"Error calling '{method_key}' method. Check the additional parameters: {e}"
        )


def reshape_weights_to_cpd(weights, variable_card, parents_card):
    """
    Reshape a flat array of weights into a conditional probability distribution (CPD).
    This is the prefered method because it always close to the population mean due to the sampling appraoch.
    The alternative function is normalize_and_reshape(weights, variable_card, parents_card, tolerance=0.5, n_times=100)

    Parameters:
    - weights (numpy.ndarray): A flat array of weights.
    - variable_card (int): Cardinality (number of states) of the variable.
    - parents_card (list): List of cardinalities of the variable's parents.

    Returns:
    - numpy.ndarray: A normalized CPD array.
    
    Raises:
    - ValueError: If inputs are not valid.
    """
    # Validate inputs
    print("weights", weights)
    
    if not isinstance(weights, np.ndarray):
        if isinstance(weights, list):
            weights = np.array(weights)
        else:
            raise ValueError("weights must be a numpy ndarray or list.")
    if not isinstance(variable_card, int) or variable_card <= 0:
        raise ValueError("variable_card must be a positive integer.")
    if bool(parents_card):
        if not all(isinstance(card, int) and card >= 0 for card in parents_card):
            raise ValueError("parents_card must be a list of positive integers.")
    
    # Initialize variables for the calculation
    total_parent_states = np.prod(parents_card) if parents_card else 1
    desired_shape = (variable_card, total_parent_states)
    raveled_dshape = np.prod(desired_shape)

    # Expected weights
    #expected_size = variable_card * total_parent_states
    
    # Check if weights length matches expected size
    '''
    if len(weights) < expected_size:
        raise ValueError(f"weights size {len(weights)} is insufficient for the expected shape {desired_shape}")

    # Validate and reshape weights directly if possible
    try:
        reshaped_weights = weights[:expected_size].reshape(desired_shape)
    except ValueError as e:
        raise ValueError(f"Error reshaping weights: {e}. Ensure weights length matches expected size {expected_size}.")
    '''
    # Sampling and reshaping with random selection
    our_samples = []
    while len(our_samples) * raveled_dshape < len(weights):
        sample_indices = np.random.choice(len(weights), size=raveled_dshape, replace=False)
        sample = weights[sample_indices]
        #sample = np.sort(sample)
        reshaped_sample = sample.reshape(desired_shape)
        #reshaped_sample = np.sort(reshaped_sample)
        our_samples.append(reshaped_sample)

    # Averaging the reshaped arrays
    
    #our_samples = np.sort(our_samples)
    mean_cpd = np.mean(our_samples, axis=0)

    # Normalizing the CPD
    #mean_cpd /= mean_cpd.sum(axis=0, keepdims=True)
    # Softmax normalization of the CPD
    mean_cpd = softmax(mean_cpd)

    # Calculate statistical significance of the mean CPD
    population_mean = np.mean(weights)
    sample_mean = np.mean(mean_cpd)
    #z_score = (sample_mean - population_mean) / np.std(mean_cpd)
    
    std_dev = np.std(mean_cpd)
    if std_dev == 0:
        z_score = 0  # Or handle as appropriate
    else:
        z_score = (sample_mean - population_mean) / std_dev
        
    p_value = norm.sf(abs(z_score)) * 2  # two-tailed
    
    return mean_cpd, p_value, z_score

def remove_outliers(data, method='iqr', threshold=3):
    """
    Remove outliers from a dataset using either the z-score or IQR method.
    
    Args:
    - data (np.array): The input data from which to remove outliers.
    - method (str): Method to use for outlier detection ('z-score' or 'iqr').
    - threshold (float): The threshold value for the z-score or multiplier for the IQR.
    
    Returns:
    - non_outliers (np.array): The data with outliers removed.
    - outliers (np.array): The data points identified as outliers.
    """
    if method not in ['z-score', 'iqr']:
        raise ValueError("Method must be either 'z-score' or 'iqr'.")

    if method == 'z-score':
        zs = zscore(data)
        is_outlier = np.abs(zs) > threshold
    else:  # method == 'iqr'
        Q1, Q3 = np.percentile(data, [25, 75])
        IQR = Q3 - Q1
        lower_bound = Q1 - (IQR * threshold)
        upper_bound = Q3 + (IQR * threshold)
        is_outlier = (data < lower_bound) | (data > upper_bound)
    
    non_outliers = data[~is_outlier]
    outliers = data[is_outlier]

    return non_outliers, outliers

def minmax_process_model_weights(model):
    """
    Process the weights of a trained deep learning model.

    Parameters:
    - model: The trained deep learning model.

    Returns:
    - processed_weights: The processed weights suitable for CPD creation.
    """
    raw_weights = np.concatenate([array.flatten() for array in model.get_weights()])

    # Normalize weights to range [0, 1]
    min_weight = raw_weights.min()
    max_weight = raw_weights.max()
    processed_weights = (raw_weights - min_weight) / (max_weight - min_weight)

    return processed_weights

def softmax(x):
    """Compute softmax values for each set of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def softmax_process_model_weights(model):
    """
    Process the weights of a trained deep learning model using softmax normalization.

    Parameters:
    - model: The trained deep learning model.

    Returns:
    - processed_weights: The softmax-normalized weights suitable for CPD creation.
    """
    # Concatenate all model weights into a single 1D array
    raw_weights = np.concatenate([array.flatten() for array in model.get_weights()])
    
    # Apply softmax to normalize weights
    processed_weights = softmax(raw_weights)

    return raw_weights

def flatten_weights(model):
    """
    Process weights and flatten them into a 1D array.

    Parameters:
    - model: The trained deep learning model.

    Returns:
    - flat_weights: 1D array of flattened weights.
    """
    # Concatenate all model weights into a single 1D array
    flat_weights = np.concatenate([array.flatten() for array in model.get_weights()])
    
    return flat_weights
