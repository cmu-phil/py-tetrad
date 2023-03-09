import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-7.2.2-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import pytetrad.translate as tr

import java.util as util
import edu.cmu.tetrad.search as ts

def print_graph(alg_name, G):
    print(f"\n{alg_name}\n")
    print(G)
    print(tr.tetrad_graph_to_pcalg(G))
    print(tr.tetrad_graph_to_causal_learn(G))

df = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_to_tetrad(df)
# print(data)

variables = data.getVariables()

score = ts.SemBicScore(data)
score.setPenaltyDiscount(2)
score.setStructurePrior(0)

test = ts.IndTestScore(score, data)
test.setAlpha(0.01)

fges = ts.Fges(score)
fges.setVerbose(True)
fges_graph = fges.search()
print_graph('FGES', fges_graph)

boss = ts.Boss(test, score)
boss.setUseDataOrder(False)
boss.setNumStarts(5)
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

datasets = util.ArrayList()
datasets.add(data)
rskew = ts.Lofs2(fges_graph, datasets)
rskew.setRule(ts.Lofs2.Rule.RSkew)
gango_graph = rskew.orient()
print_graph('GANGO', gango_graph)

pc = ts.Pc(test)
pc_graph = pc.search()
print_graph('PC', pc_graph)

fci = ts.Fci(test)
fci_graph = fci.search()
print_graph('FCI', fci_graph)

gfci = ts.GFci(test, score)
gfci_graph = gfci.search()
print_graph('GFCI', gfci_graph)

grasp_fci = ts.GraspFci(test, score)
grasp_fci_graph = grasp_fci.search()
print_graph('GRaSP-FCI', grasp_fci_graph)
