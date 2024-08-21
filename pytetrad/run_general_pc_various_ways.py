
from jpype import JImplements, JOverride
import jpype.imports
import time

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import pandas as pd

import tools.translate as tr

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search.test as tt

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
df = df.sample(600, replace=True) # bootstrap sample.
df = df.astype({col: "float64" for col in df.columns})

# Run Tetrad's PC using causal-learn's KCI
# For this we'll need to wrap causal-learn's KCI in a JPype object so that
# Tetrad can use it.
def run_tetrad_pc_using_cl_kci():

    @JImplements(ts.IndependenceTest)
    class KciWrapper:
        def __init__(self, df, alpha = alpha_):
            self.df = df
            self.data = df.values
            self.alpha = alpha
            self.kci_obj = CIT(self.data, "kci")

            self.variables = util.ArrayList()
            self.variable_map = {}
            self.reverse_variable_map = {}

            for col in df.columns:
                col = str(col)
                variable = td.ContinuousVariable(col)
                self.variables.add(variable)
                self.variable_map[col] = variable
                self.reverse_variable_map[variable] = df.columns.get_loc(col)

        @JOverride
        def checkIndependence(self, *args):
            x = args[0]
            y = args[1]
            s = args[2]
            fact = tg.IndependenceFact(x, y, s)

            # Convert x, y, s to indices using the reverse map
            X = self.reverse_variable_map[x]
            Y = self.reverse_variable_map[y]
            S = [self.reverse_variable_map[si] for si in s]

            pValue = self.kci_obj(X, Y, S)
            indep = pValue > self.alpha

            result = tt.IndependenceResult(fact, indep, pValue, self.alpha - pValue)
            return result

        @JOverride
        def getVariables(self, *arg):
            return self.variables

        @JOverride
        def getData(self, *arg):
            return tr.pandas_data_to_tetrad(self.df)

        @JOverride
        def isVerbose(self, *arg):
            return False

        @JOverride
        def setVerbose(self, *arg):
            pass

        @JOverride
        def toString(self, *arg):
            return "KCI-Wrapper"

    start_time = time.time()
    test1 = KciWrapper(df)
    pc = ts.Pc(test1)
    pc.setVerbose(False)
    graph = pc.search()
    end_time = time.time()

    print("\nTetrad PC w/ JPype wrapper of causal-learn's KCI", graph)
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

# Run CL's PC using CL's KCI
def run_cl_pc_using_cl_kci():

    start_time = time.time()
    cg = pc(df.values, alpha_, kci, node_names=df.columns)
    end_time = time.time()

    print("\nCL PC with CL's KCI", cg.G)
    print("Time taken", end_time - start_time)

run_cl_pc_using_cl_kci()
run_tetrad_pc_using_cl_kci()

# Way too slow; need to optimize this.
# run_tetrad_pc_using_tetrad_kci()
