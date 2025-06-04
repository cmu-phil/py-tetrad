# This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd
import pytetrad.tools.TetradSearch as ts

data = pd.read_csv("resources/bridges.data.version211_rev.txt", sep="\t")

## Make a TetradSearch instance to run searches against. This helps to organize
## the use of Tetrad search algorithms and hides the JPype code for those who
## don't want to deal with it.
search = ts.TetradSearch(data)
search.set_verbose(False)

## Pick the score to use, in this case a continuous linear, Gaussian score.
search.use_bdeu(sample_prior=10, structure_prior=0)
search.use_chi_square(alpha=0.1)

## Run various algorithms and print their results. For now (for compability with R)
## Commenting out the ones that won't work with discrete data.
print('FGES')
search.run_fges()
print(search.get_string())

print('BOSS')
search.run_boss()
print(search.get_string())

# print('SP')
# search.run_sp()
# print(search.get_string())

print('GRaSP')
search.run_grasp()
print(search.get_string())

# print('GANGO', gango_graph)
# search.run_gango()
# print(search.get_string())

print('PC')
search.run_pc()
print(search.get_string())

print('FCI')
search.run_fci()
print(search.get_string())

print('GFCI')
search.run_gfci()
print(search.get_string())

print('BFCI')
search.run_boss_fci()
print(search.get_string())

print('GRaSP-FCI')
search.run_grasp_fci()
print(search.get_string())

# print('CCD')
# search.run_ccd()
# print(search.get_string())

# print('SVAR-FCI')
# search.run_svar_fci()
# print(search.get_string())
