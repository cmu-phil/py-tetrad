import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

from pytetrad.util import startJVM
startJVM()

import pandas as pd
import pytetrad.translate as tr

import edu.cmu.tetrad.search as ts

def print_graph(alg_name, G):
    print(f"\n{alg_name}\n")
    print(G)
    print(tr.tetrad_graph_to_pcalg(G))
    print(tr.tetrad_graph_to_causal_learn(G))

df = pd.read_csv(f"{BASE_DIR}/examples/resources/auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns if col != "origin"})

data = tr.pandas_to_tetrad(df)

variables = data.getVariables()

# Note: This API is confusing in Tetrad; need to clean it up for the next version of Tetrad
# so these mixed variable tests and scores can be called more simply.

score = ts.SemBicScoreDGWrapper(data)
score.setPenaltyDiscount(2)
score.setStructurePrior(0)

test = ts.IndTestScore(score, data)
test.setAlpha(0.01)

fges = ts.Fges(score)
fges_graph = fges.search()
print_graph('fGES', fges_graph)

boss = ts.Boss(test, score)
boss.setUseDataOrder(False)
boss.setNumStarts(1)
boss.bestOrder(variables)
boss_graph = boss.getGraph(True)
print_graph('BOSS', boss_graph)

grasp = ts.Grasp(test, score)
grasp.setOrdered(False)
grasp.setUseDataOrder(False)
grasp.setNumStarts(5)
grasp.bestOrder(variables)
grasp_graph = grasp.getGraph(True)
print_graph('GRaSP', grasp_graph)

fci = ts.Fci(test)
fci_graph = fci.search()
print_graph('FCI', fci_graph)

gfci = ts.GFci(test, score)
gfci_graph = gfci.search()
print_graph('GFCI', gfci_graph)

grasp_fci = ts.GraspFci(test, score)
grasp_fci_graph = grasp_fci.search()
print_graph('GRaSP-FCI', grasp_fci_graph)
