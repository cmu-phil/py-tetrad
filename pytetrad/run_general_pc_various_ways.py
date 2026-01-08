# This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

# This script runs PC using a general score in various ways: (1) using causal-learn's KCI in Tetrad,
# (2) using causal-learn's KCI in causal-learn, and (3) using Tetrad's KCI in Tetrad.

import time

import pytetrad.tools.translate as tr
from pytetrad.tools import WrappedClKci as wc
import pytetrad.tools.TetradSearch as tetrads

import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.test as tt
import pandas as pd

from pytetrad.tools import WrappedClKci as wc

try:
    from causallearn.utils.cit import CIT
    from causallearn.search.ConstraintBased.PC import pc
    from causallearn.utils.cit import kci
except ImportError as e:
    print('Could not import a causal-learn module: ', e)

# Set the alpha level for the independence tests
alpha_ = 0.001
approx = True
nullss = 1000
kernel = 'Gaussian'
polyd = 2
timeout=500

# Grab the airfoil data (a small problem with just 6 variables)
df = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
# df = pd.read_csv(f"/Users/josephramsey/Downloads/data_nonlinear.csv")
# df = pd.read_csv(f"resources/diabetes.data.d.txt", sep="\t")
df = df.sample(800, replace=True)  # bootstrap sample.
df = df.astype({col: "float64" for col in df.columns})


# Run Tetrad's PC using Tetrad's KCI
def printMcResult(graph, data):
    _search = tetrads.TetradSearch(data)
    _search.use_kci(use_for_mc=True)
    _search.use_test(wc.WrappedClKci(data, alpha=0.01), use_for_mc=True)
    ad_ind, ad_dep, ks_ind, ks_dep, bin_indep, bin_dep, frac_dep_ind, frac_dep_dep, num_tests_ind, num_tests_dep, mc \
        = _search.markov_check(graph, parallelized=True, effective_sample_size=-1)

    print()
    print(f"AD p-value Indep = {ad_ind:5.4} Dep = {ad_dep:5.4}")
    print(f"Fraction dependent Indep = {frac_dep_ind:5.4} Dep = {frac_dep_dep:5.4}")
    print(f"Num tests Indep = {num_tests_ind} Dep = {num_tests_dep}")

# Run CL's PC using CL's KCI
def run_cl_pc_using_cl_kci():
    start_time = time.time()
    cg = pc(df.values, alpha_, kci, node_names=df.columns)
            # , node_names=df.columns, kernelX=kernel, kernelY=kernel, nullss=nullss,
            # approx=approx, est_width='median', polyd=polyd)
    end_time = time.time()

    print("\nCL PC with CL's KCI", cg.G)
    print("Time taken", end_time - start_time)

    # ad_p = getMarkovCheckerP(cg, df)
    #
    # print("AD P = " + str(ad_p))

# Run Tetrad's PC using causal-learn's KCI.
# For this we'll need to wrap causal-learn's KCI in a JPype object so that
# Tetrad can use it.
# We need to use the non-stable version of PC to avoid parallelization.
def run_tetrad_pc_using_cl_kci(timeout=-1):

    import numpy as np

    shuffled_columns = np.random.permutation(df.columns)
    df_ = df[shuffled_columns]

    start_time = time.time()

    test1 = wc.KciWrapper(df_, start_time=start_time, timeout=timeout,
                          alpha=alpha_, kernelX=kernel, kernelY=kernel, nullss=nullss,
                          approx=approx, est_width='median', polyd=polyd)
    pc = ts.Pc(test1)
    pc.setVerbose(True)
    pc.setFasStable(False)
    pc.setTimeoutMs(timeout * 1000)
    graph = pc.search()
    end_time = time.time()

    print("Tetrad PC w/ JPype wrapper of causal-learn's KCI", graph)
    print("Time taken", end_time - start_time)

    printMcResult(graph, df)

def run_tetrad_pc_using_tetrad_kci():
    start_time = time.time()
    data = tr.pandas_data_to_tetrad(df)
    test1 = tt.Kci(data)
    test1.setAlpha(alpha_)
    # test1.setApproximate(approx)

    if kernel == 'Gaussian':
        test1.setKernelType(tt.Kci.KernelType.GAUSSIAN)
        # test1.setScalingFactor(1)
    elif kernel == 'Linear':
        test1.setKernelType(tt.Kci.KernelType.LINEAR)
    elif kernel == 'Polynomial':
        test1.setKernelType(tt.Kci.KernelType.POLYNOMIAL)
        test1.setPolyDegree(polyd)
    else:
        raise ValueError(f"Unknown kernel type: {kernel}")

    # test1.setNumPermutations(nullss)
    pc = ts.Pc(test1)
    pc.setVerbose(True)
    # pc.setFasStable(True)
    # pc.setDepth(-1)
    graph = pc.search()
    end_time = time.time()

    print("Tetrad PC with Tetrad's KCI", graph)
    print("Time taken", end_time - start_time)

    ad_p = printMcResult(graph, df)

# run_cl_pc_using_cl_kci()
# run_tetrad_pc_using_cl_kci(timeout=timeout)
run_tetrad_pc_using_tetrad_kci()
