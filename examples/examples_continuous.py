import os
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

import jpype
import jpype.imports

# os.environ["JAVA_HOME"] = "/usr/libexec/java_home"
jpype.startJVM(classpath=[f"{BASE_DIR}/tetrad-gui-7.2.2-launch.jar"])

import pandas as pd
import pytetrad.translate as tr

import java.util as util
import edu.cmu.tetrad.search as ts


df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.data_frame_to_tetrad_data(df)
print(data)

variables = data.getVariables()

score = ts.SemBicScore(data)
score.setPenaltyDiscount(2)
score.setStructurePrior(0)

print("\nfGES\n")
fges = ts.Fges(score)
fges_graph = fges.search()

print("\nBOSS\n")
boss = ts.Boss(score)
boss.setUseDataOrder(False)
boss.setNumStarts(5)
boss.bestOrder(variables)
boss_graph = boss.getGraph(True)

print("\nGRaSP\n")
grasp = ts.Grasp(score)
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

print(fges_graph)
print(boss_graph)
print(grasp_graph)
print(gango_graph)

print(tr.tetrad_graph_to_pcalg(fges_graph))
print(tr.tetrad_graph_to_pcalg(boss_graph))
print(tr.tetrad_graph_to_pcalg(grasp_graph))
print(tr.tetrad_graph_to_pcalg(gango_graph))

print(tr.tetrad_graph_to_causal_learn(fges_graph))
print(tr.tetrad_graph_to_causal_learn(boss_graph))
print(tr.tetrad_graph_to_causal_learn(grasp_graph))
print(tr.tetrad_graph_to_causal_learn(gango_graph))
