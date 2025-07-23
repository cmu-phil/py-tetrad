# This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd

import pytetrad.tools.TetradSearch as ts

data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
# data = pd.read_csv("resources/sample_lng_data_10_2_1000.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

print(data)

## Make a TetradSearch instance to run searches against. This helps to organize
## the use of Tetrad search algorithms and hides the JPype code for those who
## don't want to deal with it.
search = ts.TetradSearch(data)
search.set_verbose(False)

## Pick the score to use, in this case a continuous linear, Gaussian score.
search.use_sem_bic()
search.use_fisher_z(alpha=0.05)

search.set_forbidden("Frequency", "Attack")

## Run various algorithms and print their results. For now (for compability with R)
print('FGES')
search.run_fges()
print(search.get_graph_to_matrix())

print('BOSS')
search.run_boss(num_starts=1, use_bes=True, time_lag=0, use_data_order=True)
print(search.get_string())
dag = search.get_dag_java()
print(dag)

search.run_boss()
adj = search.get_graph_to_matrix()

print(adj)

print('SP')
search.run_sp()
print(search.get_string())

print('GRaSP')
search.run_grasp()
print(search.get_string())

print('PC')
search.run_pc()
print(search.get_string())

print('PC-Max')
search.run_pc_max()
print(search.get_string())

print('CPC')
search.run_cpc()
print(search.get_string())

print('FCI')
search.run_fci()
print(search.get_string())

print('FCI-Max')
search.run_fci_max()
print(search.get_string())

print('CFCI')
search.run_cfci()
print(search.get_string())

print('GFCI')
search.run_gfci()
print(search.get_string())

print('FCIT')
search.run_fcit()
print(search.get_string())

print('GRaSP-FCI')
search.run_grasp_fci()
print(search.get_string())

print('BOSS-FCI')
search.run_boss_fci()
print(search.get_string)

print('BOSS-POD')
search.run_boss_pod()
print(search.get_string)

print('CCD')
search.run_ccd()
print(search.get_string())

print('SVAR-GFCI')
search.run_svar_gfci()
print(search.get_string())

print('SP-FCI')
search.run_spfci()
print(search.get_string())

print('ICA-LiNGAM')
search.run_ica_lingam(threshold_b=0.06)
print(search.get_string())
print('bhat:')
print(search.get_bhat())

print('FASK')
search.run_fask()
print(search.get_string())

## Set verbose to True to print unstable models; otherwise, only stable models will be printed.
print('ICA-LiNG-D')
search.set_verbose(False)
search.run_ica_lingd(threshold_w=1e-4)
print('unstable bhats:')
print(search.get_unstable_bhats())
print('stable bhats:')
print(search.get_stable_bhats())


## The algorithm will return one of the stable models, or an empty graph if there is none. But the above should
## print all of the stable models if verbose is set to False.
# print(search.get_string())
