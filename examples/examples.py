import pandas as pd
import pytetrad.Translate as tr

# os.environ["JAVA_HOME"] = "/usr/libexec/java_home"
# jpype.startJVM(classpath=["/Users/josephramsey/Downloads/tetrad-gui-7.2.2-launch.jar"])

import edu.cmu.tetrad.search as ts

import java.util as util

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")

data = tr.data_frame_to_tetrad_data(df)
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
