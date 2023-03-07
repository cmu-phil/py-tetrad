import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

import jpype
import jpype.imports

# this needs to happen before import pytetrad (otherwise lib cant be found)
try:
    jpype.startJVM(classpath=[f"{BASE_DIR}/tetrad-gui-7.2.2-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import numpy as np
import pytetrad.translate as tr

import edu.cmu.tetrad.search as ts

from causallearn.search.ConstraintBased.PC import pc, pc_alg
from causallearn.utils.cit import chisq, fisherz, kci, d_separation, KCI

df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_to_tetrad(df)

print("\nCL PC\n")
cg = pc(np.array(df), 0.05, fisherz, node_names=df.columns)
print(cg.G)

print("\nTetrad PC\n")
test = ts.IndTestFisherZ(data, 0.05)
tetrad_pc = ts.Pc(test)
tetrad_pc_graph = tetrad_pc.search()

print(tetrad_pc_graph)
