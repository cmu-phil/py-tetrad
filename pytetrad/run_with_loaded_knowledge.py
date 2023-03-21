import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-7.3.0-launch.jar"])
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

import java.io as io
import edu.cmu.tetrad.data as td

know_file = io.File("resources/knowledge.txt")
know_delim = td.DelimiterType.WHITESPACE
kwnl = td.SimpleDataLoader.loadKnowledge(know_file, know_delim, "//")

print(kwnl)

fges_graph = search.fges(score, knowledge=kwnl)
print('FGES', fges_graph)

grasp_graph = search.grasp(score, knowledge=kwnl)
print('GRaSP', grasp_graph)

gango_graph = search.gango(score, data, knowledge=kwnl)
print('GANGO', gango_graph)

pc_graph = search.pc(test, knowledge=kwnl)
print('PC', pc_graph)

fci_graph = search.fci(test, knowledge=kwnl)
print('FCI', fci_graph)

gfci_graph = search.gfci(test, score, knowledge=kwnl)
print('GFCI', gfci_graph)

grasp_fci_graph = search.grasp_fci(test, score, knowledge=kwnl)
print('GRaSP-FCI', grasp_fci_graph)
