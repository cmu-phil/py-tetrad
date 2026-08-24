## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

## NOTE: IMaGES is no longer a separate algorithm in the Tetrad interface. Pooling several data
## sets that share a causal structure (what IMaGES did, via a summed score) is now a general
## capability of any score- or test-based search, requested via TetradSearch.add_data_set(...) and
## TetradSearch.set_pool_data_sets(True) -- see pooled_data_sets_example.py for the current,
## recommended way to do this. This script is kept as a low-level demonstration of the raw JPype
## API (multi.Images is still present in the jar; it is just no longer registered in the GUI's
## algorithm list), for anyone working directly against edu.cmu.tetrad.algcomparison.algorithm.multi
## rather than through TetradSearch.

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
