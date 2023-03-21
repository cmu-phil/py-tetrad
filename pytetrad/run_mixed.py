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

## We have to types of scores/tests, Conditional Gaussian and Degenerate Gaussian.
score = ts.ConditionalGaussianScore(data, 2, True)
# score = ts.DegenerateGaussianScore(data)

# test = ts.IndTestScore(score)
test = ts.IndTestConditionalGaussianLRT(data, 0.05, True)
# test = ts.IndTestDegenerateGaussianLRT(data)
# test.setAlpha(0.01)

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

bfci_graph = search.bfci(test, score)
print('BFCI', bfci_graph)

grasp_fci_graph = search.grasp_fci(test, score)
print('GRaSP_FCI', grasp_fci_graph)
