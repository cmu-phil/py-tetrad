import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

from pytetrad.util import startJVM
startJVM()

import pandas as pd
import pytetrad.translate as tr

df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_to_tetrad(df)
print(data)

data_ = tr.tetrad_to_pandas(data)
print(data_)

df = pd.read_csv(f"{BASE_DIR}/examples/resources/bridges.data.version211_rev.txt", sep="\t")

data = tr.pandas_to_tetrad(df)
print(data)

data_ = tr.tetrad_to_pandas(data)
print(data_)

df = pd.read_csv(f"{BASE_DIR}/examples/resources/auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns if col != "origin"})

data = tr.pandas_to_tetrad(df)
print(data)

data_ = tr.tetrad_to_pandas(data)
print(data_)
