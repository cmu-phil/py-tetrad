import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

from pytetrad.util import startJVM
startJVM()

import pandas as pd
import pytetrad.translate as tr

import java.util as util
import edu.cmu.tetrad.search as ts


df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_to_tetrad(df)
print(data)

variables = data.getVariables()

score = ts.SemBicScore(data)
score.setPenaltyDiscount(2)
score.setStructurePrior(0)

test = ts.IndTestScore(score, data)
test.setAlpha(0.01)

print("\nfGES\n")
fges = ts.Fges(score)
fges_graph = fges.search()

print("\nBOSS\n")
boss = ts.Boss(test, score)
boss.setUseDataOrder(False)
boss.setNumStarts(5)
boss.bestOrder(variables)
boss_graph = boss.getGraph(True)

print("\nGRaSP\n")
grasp = ts.Grasp(test, score)
grasp.setOrdered(False)
grasp.setUseDataOrder(False)
grasp.setNumStarts(5)
grasp.bestOrder(variables)
grasp_graph = grasp.getGraph(True)

print("\nGANGO\n")
datasets = util.ArrayList()
datasets.add(data)
rskew = ts.Lofs2(fges_graph, datasets)
rskew.setRule(ts.Lofs2.Rule.RSkew)
gango_graph = rskew.orient()

print("\nFCI\n")
fci = ts.Fci(test)
fci_graph = fci.search()

print("\nGFCI\n")
gfci = ts.GFci(test, score)
gfci_graph = gfci.search()

print("\nGRaSP-FCI\n")
grasp_fci = ts.GraspFci(test, score)
grasp_fci_graph = grasp_fci.search()

print(fges_graph)
print(boss_graph)
print(grasp_graph)
print(gango_graph)
print(fci_graph)
print(gfci_graph)
print(grasp_fci_graph)

print(tr.tetrad_graph_to_pcalg(fges_graph))
print(tr.tetrad_graph_to_pcalg(boss_graph))
print(tr.tetrad_graph_to_pcalg(grasp_graph))
print(tr.tetrad_graph_to_pcalg(gango_graph))
print(tr.tetrad_graph_to_pcalg(fci_graph))
print(tr.tetrad_graph_to_pcalg(gfci_graph))
print(tr.tetrad_graph_to_pcalg(grasp_fci_graph))

print(tr.tetrad_graph_to_causal_learn(fges_graph))
print(tr.tetrad_graph_to_causal_learn(boss_graph))
print(tr.tetrad_graph_to_causal_learn(grasp_graph))
print(tr.tetrad_graph_to_causal_learn(gango_graph))
print(tr.tetrad_graph_to_causal_learn(fci_graph))
print(tr.tetrad_graph_to_causal_learn(gfci_graph))
print(tr.tetrad_graph_to_causal_learn(grasp_fci_graph))
