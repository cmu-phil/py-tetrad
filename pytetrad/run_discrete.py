import jpype.imports

try:
   jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import tools.translate as tr
import tools.search as search

import edu.cmu.tetrad.search as ts

def print_graph(alg_name, G):
    print(f"\n{alg_name}\n")
    print(G)
    print(tr.tetrad_graph_to_pcalg(G))
    print(tr.tetrad_graph_to_causal_learn(G))

df = pd.read_csv("resources/bridges.data.version211_rev.txt", sep="\t")

data = tr.pandas_to_tetrad(df)
print(data)

# score = ts.DiscreteBicScore(data)

score = ts.BDeuScore(data)
score.setSamplePrior(10)
score.setStructurePrior(1)

test = ts.IndTestGSquare(data, 0.05)

fges_graph = search.fges(score)
print('fGES', fges_graph)

boss_graph = search.boss(score)
print('BOSS', boss_graph)

grasp_graph = search.grasp(score)
print('GRaSP', grasp_graph)

pc_graph = search.pc(test)
print('PC', pc_graph)

fci_graph = search.fci(test)
print('FCI', fci_graph)

gfci_graph = search.gfci(test, score)
print('GFCI', gfci_graph)

graph_fci_graph = search.grasp_fci(test, score)
print('GraSP-FCI', graph_fci_graph)
