# Tests some functionality that needs to work from R, in our current
# understanding (which may be naive).
#
# This may be a bit constricting for Python users, since it assumes
# you need functions that take data frames as inputs and output data
# frames (for ease of use in R), but go ahead and use it is you like.
# The functions will take pandas data frames as input, with parameters,
# and output PCALG-style general graphs.
#
# For R users, we are currently working out how this can work
# in R-Studio and will try to give updated instructions in the
# R directory. Currently under investigation.

import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import edu.cmu.tetrad.search as ts
import tools.translate as tr

def fges(data_frame, verbose=False, knowledge=None, penalty_discount = 2):
    data = tr.pandas_data_to_tetrad(data_frame)
    score = ts.SemBicScore(data)
    score.setPenaltyDiscount(penalty_discount)
    score.setStructurePrior(0)
    fges = ts.Fges(score)
    if knowledge != None:
        fges.setKnowledge(knowledge)
    fges.setVerbose(verbose)
    pattern = fges.search()
    return tr.tetrad_graph_to_pcalg(pattern)