## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd
import pytetrad.tools.translate as tr

df = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_data_to_tetrad(df)
print(data)

data_ = tr.tetrad_data_to_pandas(data)
print(data_)

df = pd.read_csv(f"resources/bridges.data.version211_rev.txt", sep="\t")

data = tr.pandas_data_to_tetrad(df)
print(data)

data_ = tr.tetrad_data_to_pandas(data)
print(data_)

df = pd.read_csv(f"resources/auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns if col != "origin"})

data = tr.pandas_data_to_tetrad(df)
print(data)

data_ = tr.tetrad_data_to_pandas(data)
print(data_)
