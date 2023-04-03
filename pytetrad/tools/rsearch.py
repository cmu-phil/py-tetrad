# Meant ot be run in R.

import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import edu.cmu.tetrad.search as ts
import tools.translate as tr

def fges(data_frame, verbose=False, knowledge=None, penalty_discount = 2):
    data = tr.pandas_to_tetrad(data_frame)
    score = ts.SemBicScore(data)
    score.setPenaltyDiscount(penalty_discount)
    score.setStructurePrior(0)
    fges = ts.Fges(score)
    if knowledge != None:
        fges.setKnowledge(knowledge)
    fges.setVerbose(verbose)
    pattern = fges.search()
    return tr.tetrad_graph_to_pcalg(pattern)