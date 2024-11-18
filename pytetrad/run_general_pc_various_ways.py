# This script run PC using a general score in various ways: (1) using causal-learn's KCI in Tetrad,
# (2) using causal-learn's KCI in causal-learn, and (3) using Tetrad's KCI in Tetrad.

import time

import jpype.imports

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

import pandas as pd

import pytetrad.tools.translate as tr

import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.test as tt
from pytetrad.tools import WrappedClKci as wc

try:
    from causallearn.utils.cit import CIT
    from causallearn.search.ConstraintBased.PC import pc
    from causallearn.utils.cit import kci
except ImportError as e:
    print('Could not import a causal-learn module: ', e)

# Set the alpha level for the independence tests
alpha_ = 0.01

# Grab the airfoil data (a small problem with just 6 variables)
df = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.sample(500, replace=True)  # bootstrap sample.
df = df.astype({col: "float64" for col in df.columns})


# Run Tetrad's PC using causal-learn's KCI
# For this we'll need to wrap causal-learn's KCI in a JPype object so that
# Tetrad can use it.
def run_tetrad_pc_using_cl_kci():
    start_time = time.time()
    test1 = wc.KciWrapper(df, alpha=alpha_)
    pc = ts.Pc(test1)
    pc.setVerbose(False)
    graph = pc.search()
    end_time = time.time()

    print("\nTetrad PC w/ JPype wrapper of causal-learn's KCI", graph)
    print("Time taken", end_time - start_time)


# Run CL's PC using CL's KCI
def run_cl_pc_using_cl_kci():
    start_time = time.time()
    cg = pc(df.values, alpha_, kci, node_names=df.columns)
    end_time = time.time()

    print("\nCL PC with CL's KCI", cg.G)
    print("Time taken", end_time - start_time)


# Run Tetrad's PC using Tetrad's KCI
def run_tetrad_pc_using_tetrad_kci():
    start_time = time.time()
    test1 = tt.Kci(tr.pandas_data_to_tetrad(df), alpha_)
    test1.setApproximate(True)
    pc = ts.Pc(test1)
    pc.setVerbose(False)
    pc.setDepth(3)
    graph = pc.search()
    end_time = time.time()

    print("\nTetrad PC with Tetrad's KCI", graph)
    print("Time taken", end_time - start_time)


run_cl_pc_using_cl_kci()
run_tetrad_pc_using_cl_kci()

# Way too slow; need to optimize this.
# run_tetrad_pc_using_tetrad_kci()
