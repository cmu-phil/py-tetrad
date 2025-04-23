# This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

# This script runs BOSS to find a CPDAG and then runs the Markov Checker on the CPDAG, comparing to the sample data.
# We show how to use either the Fisher Z test or the WrappedClKci test for the Markov Checker. The WrappedClKci test
# is a wrapper around the KCI test from causal-learn. We don't import causal-learn in our scripts by default, as some
# users cannot have it installed because its numerous dependencies. If you want to use the WrappedClKci test, you
# will need to uncomment those lines in this script and install causal-learn.

import pandas as pd
import pytetrad.tools.TetradSearch as search
# from pytetrad.tools import WrappedClKci as wc

# data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
data = pd.read_csv("resources/sample_lng_data_10_2_1000.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

_search = search.TetradSearch(data)

# Pick the score to use, in this case a continuous linear, Gaussian score.
_search.use_sem_bic(penalty_discount=1)

# Run an algorithm and grab the CPCDAG
print('BOSS')
_search.run_boss(num_starts=1, use_bes=True, time_lag=0, use_data_order=True)
cpdag = _search.get_java()
print(cpdag)

bic = cpdag.getAttribute("BIC")
print("bic", bic)

_search = search.TetradSearch(data)

# We need to choose which test to use for the Markov checker--either Fisher Z or WrappedClKci.

_search.use_fisher_z(use_for_mc=True)
# _search.use_test(wc.WrappedClKci(data, alpha=0.01), use_for_mc=True)

# Note that we have added an option to control whether parallelism is used in the Markov Checker, as we are not
# sure whether the Markov Checker is thread-safe when using the WrappedClKci test. We will test this in the future.
ad_ind, ad_dep, ks_ind, ks_dep, bin_indep, bin_dep, frac_dep_ind, frac_dep_dep, num_tests_ind, num_tests_dep, mc \
    = _search.markov_check(cpdag, parallelized=True, effective_sample_size=-1)

results = mc.getResults(True)

print("\nResults:\n")

for result in results:
    print(result)

    # Can get the fact, p-value, etc. from the result object--e.g.:
    # fact = result.getFact()
    # p_value = result.getPValue()
    # print(fact, 'p-value = ', p_value)

print()
print(f"AD p-value Indep = {ad_ind:5.4} Dep = {ad_dep:5.4}")
print(f"Fraction dependent Indep = {frac_dep_ind:5.4} Dep = {frac_dep_dep:5.4}")
print(f"Num tests Indep = {num_tests_ind} Dep = {num_tests_dep}")

