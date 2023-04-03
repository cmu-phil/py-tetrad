# Tests some functionality that needs to work from R, in our current
# understanding (which may be naive still).
#
# This may be a bit constricting for Python users, since it assumes
# you need functions that take data frames as input for data and output
# graphs in PCALG format (a data frame format), but if you're a Python
# user, go ahead and use it if you like.
#
# For R users, we are currently working out how this can work
# in R-Studio and will try to give updated instructions in the
# R directory. Currently under investigation.

import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass
    # print("JVM already started")

import tools.translate as tr
import tools.search as search
import edu.cmu.tetrad.search as ts

def fges(data_frame, verbose=False, knowledge=None, penalty_discount = 2):
    data = tr.pandas_data_to_tetrad(data_frame)
    score = ts.SemBicScore(data)
    score.setPenaltyDiscount(penalty_discount)
    score.setStructurePrior(0)
    pattern = search.fges(score, knowledge = knowledge, verbose = verbose)
    return tr.tetrad_graph_to_pcalg(pattern)

def boss(data_frame, verbose=False, knowledge=None, penalty_discount = 2, depth=-1, num_starts=1):
    data = tr.pandas_data_to_tetrad(data_frame)
    score = ts.SemBicScore(data)
    score.setPenaltyDiscount(penalty_discount)
    score.setStructurePrior(0)
    pattern = search.boss(score, knowledge = knowledge, verbose = verbose, depth=depth, num_starts= num_starts)
    return tr.tetrad_graph_to_pcalg(pattern)