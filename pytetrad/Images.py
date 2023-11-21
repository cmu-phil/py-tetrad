import sys

import jpype.imports
import pandas as pd

BASE_DIR = ".."
sys.path.append(BASE_DIR)
jpype.startJVM(classpath=[f"{BASE_DIR}/pytetrad/resources/tetrad-current.jar"])

import tools.translate as tr
import edu.cmu.tetrad.algcomparison.algorithm.multi as multi
import edu.cmu.tetrad.util as util
import java.util as jutil

### Just some boilerplate code to show how to run IMaGES using JPype. For a
### real example, one wouldn't use the same dataset twice but would load
### multiple datasets with the same variable names. Knowledge tiers can be
### used for lagged data, forbidding edges backward in time, though this is
### not demoed here.
print("IMaGES")

# Grabbing some continuous data...
df2 = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df2 = df2.astype({col: "float64" for col in df2.columns})

# IMaGES uses the SEM BIC score by default, although it could use other scores.
alg = multi.Images()
params = util.Parameters()
params.set(util.Params.PENALTY_DISCOUNT, 2)
data2 = tr.pandas_data_to_tetrad(df2)

list = jutil.ArrayList()
list.add(data2)
list.add(data2)

cpdag = alg.search(list, params)

tr.print_java(cpdag)
