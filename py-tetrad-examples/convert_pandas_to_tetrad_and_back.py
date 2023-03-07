import jpype
import jpype.imports

# this needs to happen before import pytetrad (otherwise lib cant be found)
try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-7.2.2-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import pytetrad.translate as tr

df = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_to_tetrad(df)
print(data)

data_ = tr.tetrad_to_pandas(data)
print(data_)

df = pd.read_csv(f"resources/bridges.data.version211_rev.txt", sep="\t")

data = tr.pandas_to_tetrad(df)
print(data)

data_ = tr.tetrad_to_pandas(data)
print(data_)

df = pd.read_csv(f"resources/auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns if col != "origin"})

data = tr.pandas_to_tetrad(df)
print(data)

data_ = tr.tetrad_to_pandas(data)
print(data_)
