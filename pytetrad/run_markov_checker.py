import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import pandas as pd

# We will wrap the Markov Checker in a nicer Python class at some point. -JR

import tools.translate as tr
import tools.TetradSearch as search
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.algcomparison.independence as ind_
from edu.cmu.tetrad.util import Params, Parameters

# Load in the data and make sure all columns are being interpreted as continuous.
data = pd.read_csv("resources/airfoil-self-noise.continuous.txt",
                   sep="\t")
data = data.astype({col: "float64" for col in data.columns})

# Make a TetradSearch instance to run searches against. This helps to organize
# the use of Tetrad search algorithms and hides the JPype code for those who
# don't want to deal with it.
search = search.TetradSearch(data)

# Pick the score to use, in this case a continuous linear, Gaussian score.
search.use_sem_bic(penalty_discount=1)

# Run an algorithm and grab the CPCDAG
print('BOSS')
search.run_boss(num_starts=1, use_bes=True, time_lag=0, use_data_order=True)
print(search.get_string())
cpdag=search.get_java()
print(cpdag)

# Get the test used for the Markov Checker--this test will be used to look
# to see whether p-values for conditional independence tests are distributed
# as U(0, 1). We will also get a fraction dependent number, which should be
# about equal to the alpha level of the test (if the p-values under the null
# hypothesis of independence are distributed as U(0, 1)). We can test for this
# Uniformity using a Kolmogorov-Smirnov test, comparing the actual
# distriubtion of p-values to U(0, 1). (In the future other tests may be
# added.)
# 
# We will also use it to check facts about the distribution for conditional 
# dependencies; in this case, the fraction of depependence judgments should
# be high, though not necessarily 1, since there may be some path
# cancellations.
params = Parameters()
params.set(Params.ALPHA, 0.05)
_test = ind_.FisherZ().getTest(tr.pandas_data_to_tetrad(data), params)

mc = ts.MarkovCheck(dag, _test, ts.ConditioningSetType.LOCAL_MARKOV)
mc.generateResults()    
p_ks_indep = mc.getKsPValue(True)
fd_indep = mc.getFractionDependent(True)
fd_dep = mc.getFractionDependent(False)

print("Kolmogorov-Smirnov p-value Indep = ", p_ks_indep)
print("Fraction dependent for Indep = ", fd_indep, " fraction dependent Dep = ", fd_dep)