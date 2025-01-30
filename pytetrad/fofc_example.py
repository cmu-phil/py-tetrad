## This script assumes that the user has pip-installed the pytetrad package. Here is now:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd
import pytetrad.tools.TetradSearch as ts

data = pd.read_csv("resources/fofc_data.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

print(data)

search = ts.TetradSearch(data)

# tetrad_test is 1 for Wishard, 2 for Delta (Bollen-Ting).
search.run_fofc(include_structure_model=True, tetrad_test=2, alpha=0.001, significance_checked=True)

print(search.get_java())
