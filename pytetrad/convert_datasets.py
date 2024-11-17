import jpype.imports

import os
import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), "-Xmx2g", classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

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
