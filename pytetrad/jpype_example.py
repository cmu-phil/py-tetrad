import pandas as pd

import graphviz as gviz

import jpype
import jpype.imports

jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])

import pytetrad.tools.translate as tr
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.data as td


tiers = [['age', 'gender', 'height', 'weight', 'resting_heart', 'device', 'activity'], 
         ['steps', 'heart_rate', 'calories', 'distance']]
reverse = {"---": "---",
           "o-o": "o-o",
           "<--": "-->",
           "-->": "<--",
           "<-o": "o->",
           "o->": "<-o",
           "<->": "<->"}
edgemarks = {'-->': ('none', 'empty'), 
             '<--': ('empty', 'none'), 
             '---': ('none', 'none'),
             '<->': ('empty', 'empty'),
             'o->': ('odot', 'empty'), 
             '<-o': ('empty', 'odot'), 
             'o-o': ('odot', 'odot')}

df = pd.read_csv("resources/aw-fb-pruned18.data.mixed.numeric.txt", sep="\t")

df = df[tiers[0] + tiers[1]]
df = df.astype({col: int for col in ["gender", "device", "activity"]})


knowledge = td.Knowledge()
knowledge.setTierForbiddenWithin(0, True)
for col in tiers[0]:
    knowledge.addToTier(0, col)
for col in tiers[1]:
    knowledge.addToTier(1, col)


probs = {}

reps= 100
for rep in range(reps):
    data = tr.pandas_data_to_tetrad(df.sample(frac=1, replace=True))

    score = ts.score.DegenerateGaussianScore(data)
    score.setPenaltyDiscount(2)

    test = ts.test.ScoreIndTest(score, data)
    
    # alg = ts.PermutationSearch(ts.Sp(score))
    alg = ts.SpFci(test, score)
    alg.setKnowledge(knowledge)

    g = alg.search()

    for edge in g.getEdges():
        edge = str(edge).split()
        if edge[0] < edge[2]:
            key = (edge[0], edge[2])
            arr = edge[1]
        else:
            key = (edge[2], edge[0])
            arr = reverse[edge[1]]

        if key not in probs:
            probs[key] = {}
        if arr not in probs[key]:
            probs[key][arr] = 0
        probs[key][arr] += 1.0 / reps


gdot = gviz.Graph(format='pdf', graph_attr={'outputorder': 'edgesfirst'})
for col in df.columns:
    gdot.node(col, shape='circle', fixedsize='true', style='filled', color='lightgray',
              stroke="transparent")

for key in probs:
    arrs = {arr: round(probs[key][arr], 3) for arr in probs[key]}
    print(key, arrs)

    for arr in arrs:
        alpha = hex(int(255 * probs[key][arr]))[2:]
        if len(alpha) == 1: alpha = "0" + alpha
        if arr == "<->": color = "#ff" + 2 * alpha
        else: color = "#" + 2 * alpha + "ff"
        gdot.edge(key[0], key[1], 
            arrowhead=edgemarks[arr][1], 
            arrowtail=edgemarks[arr][0],
            dir="both",
            color=color)

gdot.render(filename="apple_fitbit.png", directory=f"", cleanup=True,
            quiet=True)
gdot.clear()