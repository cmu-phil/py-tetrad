## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd
import pytetrad.tools.TetradSearch as ts

data = pd.read_csv("resources/fofc_data.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

# print(data)

search = ts.TetradSearch(data)
search.set_verbose(False)

# # tetrad_test is 1 for CCA, 2 Bollen-Ting 3 for Wishart
search.run_fofc(include_structure_model=True, tetrad_test=1, alpha=0.001)

print(search.get_java())

search.run_bpc(include_structure_model=False, alpha=0.01)

print(search.get_java())

search.run_factor_analysis()

print(search.get_java())
