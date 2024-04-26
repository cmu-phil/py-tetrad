import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import pandas as pd

# This is an example of how to use the Markov Checker.
# We will wrap the Markov Checker in a nicer Python class at some point. -JR

import tools.translate as trk
import tools.TetradSearch as search
import edu.cmu.tetrad.algcomparison.independence as ind_

# Load in the data and make sure all columns are being interpreted as continuous.
data = pd.read_csv("resources/airfoil-self-noise.continuous.txt",
                   sep="\t")
data = data.astype({col: "float64" for col in data.columns})

# Make a TetradSearch instance to run searches against. This helps to organize
# the use of Tetrad search algorithms and hides the JPype code for those who
# don't want to deal with it.
_search = search.TetradSearch(data)

# Hyperparameter settings
num_starts = 1
use_bes = True
time_lag = 0
use_data_order = True
penalty_discount = 1
alpha = 0.01

# Pick the score to use, in this case a continuous linear, Gaussian score.
_search.use_sem_bic(penalty_discount=penalty_discount)

# Run an algorithm and grab the CPCDAG
print('BOSS')
_search.run_boss(num_starts=num_starts, use_bes=use_bes, time_lag=time_lag,
                 use_data_order=use_data_order)
cpdag = _search.get_java()
print(cpdag)

bic = cpdag.getAttribute("BIC")
print("bic", bic)

# Get the test used for the Markov Checker--this test will be used to look
# to see whether p-values for conditional independence tests are distributed
# as U(0, 1). We will also get a fraction dependent number, which should be
# about equal to the alpha level of the test (if the p-values under the null
# hypothesis of independence are distributed as U(0, 1)). We can test for this
# Uniformity using an Anderson-Darling (AD) test or a Binomial (bin) test.
# 
# We will also use it to check facts about the distribution for conditional 
# dependencies; in this case, the fraction of dependence judgments should
# be high, though not necessarily 1, since there may be some path
# cancellations.

_search = search.TetradSearch(data)

# This test is used to check Markov
_search.use_fisher_z()
ad_ind, ad_dep, bin_indep, bin_dep, frac_dep_ind, frac_dep_dep, num_tests_ind, num_tests_dep, mc = _search.markov_check(
    cpdag)

print(f"AD p-value Indep = {ad_ind:5.4} Dep = {ad_dep:5.4}")
print(f"Bin p-value Indep = {bin_indep:5.4} Dep = {bin_dep:5.4}")
print(f"Fraction dependent Indep = {frac_dep_ind:5.4} Dep = {frac_dep_dep:5.4}")
print(f"Num tests Indep = {num_tests_ind} Dep = {num_tests_dep}")

results = mc.getResults(True)

for result in results:
    print(result)
    fact = result.getFact()
    x = fact.getX()
    y = fact.getY()

    x_name = x.getName()
    y_name = y.getName()

    p_value = result.getPValue()

    print('x = ', x_name)
    print('y = ', y_name)
    print('p-value = ', p_value)
