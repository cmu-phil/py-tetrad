import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import tools.translate as tr
import tools.search as search

import edu.cmu.tetrad.search as ts

# data, graph = sim.simulateLeeHastie()

df = pd.read_csv("resources/auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns if col != "origin"})

data = tr.pandas_to_tetrad(df)

score = ts.ConditionalGaussianScore(data, 2, True)

# score = ts.DegenerateGaussianScore(data)
# score.setPenaltyDiscount(2)
# score.setStructurePrior(0)

test = ts.IndTestConditionalGaussianLRT(data, 0.01, True)

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

gfci_graph = search.grasp_fci(test, score)
print('GFCI', gfci_graph)
