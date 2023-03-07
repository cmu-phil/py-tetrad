import os
import sys
import time

# this needs to happen before import pytetrad (otherwise lib cant be found)
import jpype
import jpype.imports

# this needs to happen before import pytetrad (otherwise lib cant be found)
try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-7.2.2-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import numpy as np

from causallearn.search.ConstraintBased.PC import pc, pc_alg
from causallearn.utils.cit import chisq, fisherz, kci, d_separation, KCI
import edu.cmu.tetrad.search as ts
import pytetrad.translate as tr
import pytetrad.simulate as util

D = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
D = D.astype({col: "float64" for col in D.columns})

# Bootstrap sample
D = D.sample(600, replace=True)
D = D.astype({col: "float64" for col in D.columns})

# D, G = util.simulateContinuous(num_meas=5, avg_deg=2, samp_size=600)
# D = D.astype({col: "float64" for col in D.columns})

# print(D)
# print(D.columns)
# print(G)

# print(np.array(D))

# numvars = data_.shape[1]

# cl_kci = cit.CIT(D, 'kci')  # , kernelX=kernelname, kernelY=kernelname,
# kernelZ=kernelname, est_width=est_width, use_gp=use_gp, approx=approx,
# polyd=polyd, kwidthx=kwidth, kwidthy=kwidth, kwidthz=kwidth)

# kci_ = KCI(np.array(D))
#
# print(f"{0} {1} {cl_kci(0, 1)}")
# print(f"{0} {1} | {2} {cl_kci(0, 1, {2})}")

print("\nCL PC\n")
start = time.time()
cg = pc(np.array(D), 0.05, kci, node_names=D.columns)
stop = time.time()
print(cg.G, stop - start)

print("\nTetrad PC\n")
start = time.time()
test = ts.Kci(tr.pandas_to_tetrad(D), 0.05)
test.setApproximate(False)
tetrad_pc = ts.Pc(test)
tetrad_pc.setVerbose(True)
tetrad_pc.setDepth(3)
tetrad_pc_graph = tetrad_pc.search()
stop = time.time()
print(tetrad_pc_graph, stop - start)

data = tr.pandas_to_tetrad(D)

variables = data.getVariables()

score = ts.SemBicScore(data)
score.setPenaltyDiscount(2)
score.setStructurePrior(0)

test = ts.IndTestScore(score, data)
test.setAlpha(0.01)

print('BOSS')
start = time.time()
boss = ts.Boss(test, score)
boss.setUseDataOrder(False)
boss.setNumStarts(5)
boss.bestOrder(variables)
boss_graph = boss.getGraph(True)
print(boss_graph, stop - start)