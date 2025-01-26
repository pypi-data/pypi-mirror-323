# DeepParameters - Integrating Deep Learning and Bayesian Networks

**DeepParameters** is a Python library for learning Bayesian Network parameters -- Conditional Probability Distributions (CPDs) -- using deep learning models. The package is highly flexibile allowing for multiple parameters to learn Bayesian network parameters.

## Installation

```bash
pip install DeepParameters
```

A DEFAULT_DIR is set up by default as `outputs/`, use bash command:

```bash
export DEFAULT_DIR=/path/to/custom/directory
```
On windows:

```bash
set DEFAULT_DIR=C:\path\to\custom\directory
```

## Dependencies

bng has the following non-optional dependencies:

- numpy
- pandas
- pgmpy
- matplotlib
- sklearn
- pickle
- os
- pathlib
- datetime
- json
- scipy
- tensorflow
- networkx
- keras
- tensorflow-probability


## Usage/Examples

The main function is **learn_cpd_for_node**

Then function is used to create a probabilistic graphical model (PGM) and accompanying sample data.

**Parameters**:
```python
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
    - network_type (str): The type of deep learning network to use. Options include 'naive', 'simple', 'medium', 'large', 'bnn'.
    - sampling_method (str): The method to use for sampling the learned weights. Options include '1', '2', '3', '4'.
    
    Accepted formats:
        * '1', '2', '3', '4'
        * Full method names ('weighted', 'stratified', 'kde', 'bayesian')
        * First letters ('w', 's', 'k', 'b')
    
    Returns:
    - A TabularCPD object for the node.
```

**Returns**:
```
dict: Dictionary containing the model, samples, and runtime.
```

```python
from DeepParameters.LearnDeepLearningCPDs import learn_cpd_for_node

# Define a simple Bayesian Network
model = BayesianNetwork([('A', 'B'), ('B', 'C')])

# Define CPDs for the model
cpd_a = TabularCPD(variable='A', variable_card=2, values=[[0.6], [0.4]])
cpd_b = TabularCPD(variable='B', variable_card=2, values=[[0.6, 0.4], [0.5, 0.5]], evidence=['A'], evidence_card=[2])
cpd_c = TabularCPD(variable='C', variable_card=2, values=[[0.9, 0.4], [0.1, 0.6]], evidence=['B'], evidence_card=[2])

# Add CPDs to the model
model.add_cpds(cpd_a, cpd_b, cpd_c)

# Verify the model
assert model.check_model()

# Generate sample data from the model
sampler = BayesianModelSampling(model)
data = sampler.forward_sample(size=1000)

# Learn CPD for node 'B'
cpd_b_learned = learn_cpd_for_node('B', data, model, model, num_parameters=10, network_type='autoencoder', sampling_method="4")

print("Learned CPD for node 'B':")
print(cpd_b_learned)


```
```python
Generating for node: C: 100%
 3/3 [00:00<00:00, 33.39it/s]
Epoch 1/10
24/24 ━━━━━━━━━━━━━━━━━━━━ 4s 62ms/step - accuracy: 0.5176 - kl_divergence: 0.5771 - loss: 0.6213 - val_accuracy: 0.5750 - val_kl_divergence: 0.2780 - val_loss: 0.6081
Epoch 2/10
24/24 ━━━━━━━━━━━━━━━━━━━━ 1s 29ms/step - accuracy: 0.4230 - kl_divergence: 0.1474 - loss: 0.6355 - val_accuracy: 0.5750 - val_kl_divergence: 4.6373e-05 - val_loss: 0.5593
Epoch 3/10
24/24 ━━━━━━━━━━━━━━━━━━━━ 0s 18ms/step - accuracy: 0.4687 - kl_divergence: 2.6430e-05 - loss: 1.1652 - val_accuracy: 0.3750 - val_kl_divergence: -1.7157e-06 - val_loss: 0.6282
Epoch 4/10
24/24 ━━━━━━━━━━━━━━━━━━━━ 1s 24ms/step - accuracy: 0.4434 - kl_divergence: -1.7775e-06 - loss: 8.0636 - val_accuracy: 0.3750 - val_kl_divergence: -1.7728e-06 - val_loss: 0.6203
Epoch 4: early stopping
learned_weights [0.015625 0.015625 0.015625 0.015625 0.015625 0.015625 0.015625 0.015625
 0.015625 0.015625]
learned_weights [0.015625 0.015625 0.015625 0.015625 0.015625 0.015625 0.015625 0.015625
 0.015625 0.015625]
Learned CPD for node 'B':
+------+---------------------+--------------------+
| A    | A(0)                | A(1)               |
+------+---------------------+--------------------+
| B(0) | 0.5000000112159115  | 0.499999977353993  |
+------+---------------------+--------------------+
| B(1) | 0.49999998878408836 | 0.5000000226460071 |
+------+---------------------+--------------------+
```

## Citing

Please use the following bibtex for citing bng in your research:

@{mulaudzi2024deepparameters,
  title={DeepParameters: Bayesian Network parameter learning using Deep Learning in Python},
  author={Mulaudzi, Rudzani},
  year={2024},
  organization={University of Witwaterand}
}

## Licensing

bng is released under MIT License. 





## Contributing

Coming soon. Email rudzani.mulaudzi2@students.wits.ac.za

