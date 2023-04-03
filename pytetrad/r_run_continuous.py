# Runs tools/rsearch algorithms, which are meant ot be run in R but checked
# here.
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import pytetrad.tools.rsearch as rs

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

G = rs.fges(df)

print(G)


