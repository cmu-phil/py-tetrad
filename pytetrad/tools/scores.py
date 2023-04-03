import jpype
import jpype.imports
import pandas as pd

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass
    # print("JVM already started")

import edu.cmu.tetrad.search as search
import tools.search as ts

import pytetrad.tools.translate as tr


## Some functions wrapping various scores in Tetrad. Feel free to just steal
## the relevant code for your own projects, or call these functions. We
## will add more named parameters to help one see which methods for the
## the searches can be controlled.

def sem_bic_score(data_frame, penaltyDiscount=2) :
    data = tr.pandas_data_to_tetrad(data_frame)
    score = search.SemBicScore(data, penaltyDiscount)
    return score
