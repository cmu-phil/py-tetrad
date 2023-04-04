# Runs tools/rsearch algorithms, which are meant ot be run in R but checked
# here.
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import pytetrad.tools.R_search as rs
import edu.cmu.tetrad.search as ts

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

print('FGES SEM BIC')
print(rs.fges(df))

print('BOSS SEM BIC')
print(rs.boss(df))


