import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import tools.translate as tr
import tools.search as search

import edu.cmu.tetrad.search as ts

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_to_tetrad(df)
# print(data)

score = ts.SemBicScore(data)
score.setPenaltyDiscount(2)
score.setStructurePrior(0)

test = ts.IndTestScore(score, data)
test.setAlpha(0.01)

fges_graph = search.fges(score)
print('FGES', fges_graph)

boss_graph = search.boss(score)
print('BOSS', boss_graph)

sp_graph = search.sp(score)
print('SP', sp_graph)

grasp_graph = search.grasp(score)
print('GRaSP', grasp_graph)

gango_graph = search.gango(score, data)
print('GANGO', gango_graph)

pc_graph = search.pc(test)
print('PC', pc_graph)

fci_graph = search.fci(test)
print('FCI', fci_graph)

gfci_graph = search.gfci(test, score)
print('GFCI', gfci_graph)

grasp_fci_graph = search.grasp_fci(test, score)
print('GRaSP-FCI', grasp_fci_graph)

## By request, an SVAR-FCI exmaple. 2023/03/23 JR
## For an applied example, data should be a time series.
## Please make an issue in the GitHub Issue Tracker if more detail is needed.
num_lags = 2
lagged_data = ts.TimeSeriesUtils.createLagData(data, num_lags)
ts_test = ts.IndTestFisherZ(lagged_data, 0.01)
svar_fci = ts.SvarFci(ts_test)
svar_fci.setKnowledge(lagged_data.getKnowledge())
svar_fci.setVerbose(True)
svar_fci_graph = svar_fci.search()
print('SVAR-FCI', svar_fci_graph)
