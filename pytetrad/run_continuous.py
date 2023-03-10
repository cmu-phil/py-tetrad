import jpype.imports

from tools.search import fges

try:
    # jpype.startJVM(classpath=[f"resources/tetrad-gui-7.2.2-launch.jar"])
    jpype.startJVM(classpath=[f"resources/tetrad-gui-bugfix-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import tools.translate as tr

import java.util as util
import edu.cmu.tetrad.search as ts

def run_searches(df):
    data = tr.pandas_to_tetrad(df)
    # print(data)

    score = ts.SemBicScore(data)
    score.setPenaltyDiscount(2)
    score.setStructurePrior(0)

    test = ts.IndTestScore(score, data)
    test.setAlpha(0.01)

    fges_graph = fges(score)
    print('FGES', fges_graph)

    boss_graph = fges(score)
    print('BOSS', boss_graph)

    grasp = ts.Grasp(test, score)
    grasp.setOrdered(False)
    grasp.setUseDataOrder(False)
    grasp.setNumStarts(5)
    grasp.bestOrder(score.getVariables())
    grasp_graph = grasp.getGraph(True)
    print('GRaSP', grasp_graph)

    datasets = util.ArrayList()
    datasets.add(data)
    rskew = ts.Lofs2(fges_graph, datasets)
    rskew.setRule(ts.Lofs2.Rule.RSkew)
    gango_graph = rskew.orient()
    print('GANGO', gango_graph)

    pc = ts.Pc(test)
    pc_graph = pc.search()
    print('PC', pc_graph)

    fci = ts.Fci(test)
    fci_graph = fci.search()
    print('FCI', fci_graph)

    gfci = ts.GFci(test, score)
    gfci_graph = gfci.search()
    print('GFCI', gfci_graph)

    grasp_fci = ts.GraspFci(test, score)
    grasp_fci_graph = grasp_fci.search()
    print('GRaSP-FCI', grasp_fci_graph)

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

run_searches(df)