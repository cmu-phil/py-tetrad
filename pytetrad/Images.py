## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)

import pytetrad.tools.translate as tr
import edu.cmu.tetrad.algcomparison.algorithm.multi as multi
import edu.cmu.tetrad.util as util
import java.util as jutil

### Just some boilerplate code to show how to run IMaGES using JPype. For a
### real example, one wouldn't use the same dataset twice but would load
### multiple datasets with the same variable names. Knowledge tiers can be
### used for lagged data, forbidding edges backward in time, though this is
### not demoed here.
###
### IMaGES runs GES with a composite score. The score at each step in GES
### is obtained by doing a scoring operation on each dataset supplied
### and then averaging these scores.
###
### BOSS could be substituted for FGES for greater accuracy, though this is
### not implemented with the current Tetrad jar. (BOSS is still new, as of
### Neurips 2023, but it is included in this jar.)
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
