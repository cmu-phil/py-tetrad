## This script assumes that the user has pip-installed the pytetrad package. Here is now:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd
import pytetrad.tools.TetradSearch as ts

data = pd.read_csv("resources/fofc_data.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

print(data)

search = ts.TetradSearch(data)
search.run_fofc(include_structure_model=True, use_wishart=False)

print(search.get_java())
