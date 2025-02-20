## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

# import graphviz as gviz
import pandas as pd

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)

import pytetrad.tools.translate as tr
import pytetrad.tools.translate as ptt
import pytetrad.tools.visualize as ptv
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.algcomparison.algorithm.multi as multi
import edu.cmu.tetrad.util as util
import java.util as jutil

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

    score = ts.score.DegenerateGaussianScore(data, True, 0.0)
    score.setPenaltyDiscount(2)
    # test = ts.test.ScoreIndTest(score, data)

    alg = ts.PermutationSearch(ts.Sp(score))
    # alg = ts.SpFci(test, score)
    alg.setKnowledge(knowledge)
    graphs.append(alg.search())

probs = ptv.graphs_to_probs(graphs)
# gdot = gviz.Graph(format="pdf", engine="neato",
#                   graph_attr={"viewport": "600",
#                               "outputorder": "edgesfirst"})
#
# gdot = ptv.write_gdot(gdot, probs, length=2)
# gdot.render(filename="apple_fitbit", cleanup=True, quiet=True)
# gdot.clear()

### Just some boilerplate code to show how to run IMaGES. For a real example,
### one wouldn't use the same dataset twice but would load multiple datasets
### with the same variable names and at least approximately the same sample
### size. Knowledge tiers can be used for lagged data, forbidding edges
### backward in time, though this is not demoed here.
print("IMaGES")

# Grabbing some continuous data...
df2 = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df2 = df2.astype({col: "float64" for col in df2.columns})

# IMaGES uses the SEM BIC score by default, although it could use other scores.
alg = multi.Images()
params = util.Parameters()
params.set(util.Params.PENALTY_DISCOUNT, 2)
data2 = tr.pandas_data_to_tetrad(df2)

list = jutil.ArrayList()
list.add(data2)
list.add(data2)

cpdag = alg.search(list, params)

dag = tg.GraphTransforms.dagFromCpdag(cpdag)
c2 = tg.GraphTransforms.dagToCpdag(dag)

tr.print_java(cpdag)
tr.print_java(c2)
