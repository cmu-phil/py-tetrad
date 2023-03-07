import os
import sys
import time

from causallearn.utils import cit

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

from causallearn.search.ConstraintBased.PC import pc, pc_alg
from causallearn.utils.cit import chisq, fisherz, kci, d_separation, KCI
import edu.cmu.tetrad.search as ts
import pytetrad.translate as tr

df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

# Bootstrap sample
df = df.sample(600, replace=True)

data = tr.pandas_to_tetrad(df)


# data_ = np.array(df)
#
# numvars = data_.shape[1]

# cl_kci = cit.CIT(data_, 'kci')  # , kernelX=kernelname, kernelY=kernelname,
# kernelZ=kernelname, est_width=est_width, use_gp=use_gp, approx=approx,
# polyd=polyd, kwidthx=kwidth, kwidthy=kwidth, kwidthz=kwidth)

# kci_ = KCI(np.array(df))

# print(f"{0} {1} {cl_kci(0, 1)}")
# print(f"{0} {1} | {2} {cl_kci(0, 1, {2})}")

# print("\nCL PC\n")
# start = time.time()
# cg = pc(np.array(df), 0.05, kci, node_names=df.columns)
# stop = time.time()
# print(cg.G, stop - start)

print("\nTetrad PC\n")
start = time.time()
test = ts.Kci(data, 0.05)
tetrad_pc = ts.Pc(test)
tetrad_pc.setVerbose(True)
tetrad_pc.setDepth(3)
tetrad_pc_graph = tetrad_pc.search()
stop = time.time()
print(tetrad_pc_graph, stop - start)