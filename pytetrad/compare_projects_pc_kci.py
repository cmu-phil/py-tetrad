import jpype.imports
import time

# this needs to happen before import pytetrad (otherwise lib cant be found)
try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import numpy as np

from causallearn.search.ConstraintBased.PC import pc
from causallearn.utils.cit import kci
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.test as test
import tools.translate as tr
import tools.search as search
import tools.simulate as sim

D = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
D = D.sample(600, replace=True) # bootstrap sample.
D = D.astype({col: "float64" for col in D.columns})

# D, G = sim.simulateContinuous(num_meas=5, avg_deg=2, samp_size=600)
# D = tr.tetrad_to_pandas(D)
# D = D.astype({col: "float64" for col in D.columns})
#
# kci_ = KCI(np.array(D))
# print(f"{0} {1} {cl_kci(0, 1)}")
# print(f"{0} {1} | {2} {cl_kci(0, 1, {2})}")

print("\nCL PC\n")
start = time.time()
cg = pc(np.array(D), 0.05, kci, node_names=D.columns)
stop = time.time()
print(cg.G, stop - start)

print("\nTetrad PC\n")
start = time.time()
test = test.Kci(tr.pandas_data_to_tetrad(D), 0.05)
test.setApproximate(False)
tetrad_pc = ts.Pc(test)
tetrad_pc.setVerbose(True)
tetrad_pc.setDepth(3)
tetrad_pc_graph = tetrad_pc.search()
stop = time.time()
print(tetrad_pc_graph, stop - start)

data = tr.pandas_data_to_tetrad(D)

variables = data.getVariables()

score = ts.SemBicScore(data)
score.setPenaltyDiscount(2)
score.setStructurePrior(0)

print('BOSS')
start = time.time()
boss_graph = search.boss(score)
stop = time.time()
print(boss_graph, stop - start)
