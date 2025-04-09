## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

# import graphviz as gviz
import pandas as pd

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)

import pytetrad.tools.translate as ptt
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.data as td

tiers = [['age', 'gender', 'height', 'weight', 'resting_heart', 'device', 'activity'],
         ['steps', 'heart_rate', 'calories', 'distance']]

df = pd.read_csv("resources/aw-fb-pruned18.data.mixed.numeric.txt", sep="\t")
df = df[tiers[0] + tiers[1]]
df = df.astype({col: int for col in ["gender", "device", "activity"]})

# Knowledge API:
# https://www.phil.cmu.edu/tetrad-javadocs/7.6.6/edu/cmu/tetrad/data/Knowledge.html

knowledge = td.Knowledge()
knowledge.setTierForbiddenWithin(0, True)
for col in tiers[0]:
    knowledge.addToTier(0, col)
for col in tiers[1]:
    knowledge.addToTier(1, col)

knowledge.setForbidden("steps", "heart_rate")
knowledge.setRequired("age", "gender")

print()
print('knowledge = ')
print()
print(knowledge)
print()

data = ptt.pandas_data_to_tetrad(df.sample(frac=1, replace=True))

score = ts.score.DegenerateGaussianScore(data, True, 0.0)
score.setPenaltyDiscount(2)

alg = ts.Fges(score)
alg.setKnowledge(knowledge)
cpdag = alg.search()
print(cpdag)
