
import numpy as np
import pandas as pd
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD

from DeepParameters import CreateDeepLearningModel as dl_model
from DeepParameters import PreprocessingData as pre_process
from DeepParameters import LearnDeepLearningCPDs as learn_cpds



def test_normalize_and_reshape():
    weights = np.random.rand(100)
    variable_card = 2
    parents_card = [2, 2]
    cpd = pre_process.normalize_and_reshape(weights, variable_card, parents_card)
    assert cpd.shape == (variable_card, np.prod(parents_card))

def test_learn_cpd_for_node():
    data = pd.DataFrame({
        'A': np.random.randint(0, 2, size=100),
        'B': np.random.randint(0, 2, size=100),
        'C': np.random.randint(0, 2, size=100)
    })
    true_model = BayesianNetwork([('A', 'C'), ('B', 'C')])
    cpd_A = TabularCPD(variable='A', variable_card=2, values=[[0.5, 0.5]])
    cpd_B = TabularCPD(variable='B', variable_card=2, values=[[0.5, 0.5]])
    cpd_C = TabularCPD(variable='C', variable_card=2, values=[[0.5, 0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5]], evidence=['A', 'B'], evidence_card=[2, 2])
    true_model.add_cpds(cpd_A, cpd_B, cpd_C)
    learnt_bn_structure = true_model
    cpd = learn_cpds.learn_cpd_for_node('C', data, true_model, learnt_bn_structure, num_parameters=10)
    assert isinstance(cpd, TabularCPD)

if __name__ == "__main__":
    test_normalize_and_reshape()
    test_learn_cpd_for_node()
    print("All tests passed.")