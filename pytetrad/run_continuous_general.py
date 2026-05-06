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
search.use_ffml()
search.use_fisher_z(alpha=0.05)

## Run various algorithms and print their results. For now (for compability with R)
print('BOSS')
search.run_boss(num_starts=1, use_bes=True, time_lag=0, use_data_order=True)
print(search.get_string())

search.use_trff_bic()
search.run_boss()
print(search.get_string())

search.use_ffci()
search.run_pc()
print(search.get_string())

