import pandas as pd
import graphviz as gviz
import sys

import jpype
import jpype.imports

BASE_DIR = ".."
sys.path.append(BASE_DIR)
jpype.startJVM(classpath=[f"{BASE_DIR}/pytetrad/resources/tetrad-gui-current-launch.jar"])

import pytetrad.tools.translate as ptt
import pytetrad.tools.visualize as ptv
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.data as td

tiers = [['age', 'gender', 'height', 'weight', 'resting_heart', 'device', 'activity'],
         ['steps', 'heart_rate', 'calories', 'distance']]

df = pd.read_csv("resources/aw-fb-pruned18.data.mixed.numeric.txt", sep="\t")
df = df[tiers[0] + tiers[1]]
df = df.astype({col: int for col in ["gender", "device", "activity"]})

knowledge = td.Knowledge()
knowledge.setTierForbiddenWithin(0, True)
for col in tiers[0]:
    knowledge.addToTier(0, col)
for col in tiers[1]:
    knowledge.addToTier(1, col)

reps = 1
graphs = []
for rep in range(reps):
    data = ptt.pandas_data_to_tetrad(df.sample(frac=1, replace=True))

    score = ts.score.DegenerateGaussianScore(data, True)
    score.setPenaltyDiscount(2)
    # test = ts.test.ScoreIndTest(score, data)

    alg = ts.PermutationSearch(ts.Sp(score))
    # alg = ts.SpFci(test, score)
    alg.setKnowledge(knowledge)
    graphs.append(alg.search())

probs = ptv.graphs_to_probs(graphs)
gdot = gviz.Graph(format="pdf", engine="neato",
                  graph_attr={"viewport": "600",
                              "outputorder": "edgesfirst"})

gdot = ptv.write_gdot(gdot, probs, length=2)
gdot.render(filename="apple_fitbit", cleanup=True, quiet=True)
gdot.clear()
