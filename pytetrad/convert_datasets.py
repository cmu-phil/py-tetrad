import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import tools.translate as tr

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
