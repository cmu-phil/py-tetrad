# This script runs the Markov Checker on a dataset using the BOSS algorithm to find a CPDAG and the KCI test from
# causal-learn, or Fisher Z, as the test for the Markov Checker. The Markov Checker is run in parallel. The script
# also prints out the results of the Markov Checker, including the p-values for each conditional independence test,
# the fraction of dependent judgments, and the number of tests run. -JR

import jpype.imports
from jpype import JImplements, JOverride

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

try:
    from causallearn.utils.cit import CIT
    from causallearn.search.ConstraintBased.PC import pc
    from causallearn.utils.cit import kci
except ImportError as e:
    print('Could not import a causal-learn module: ', e)

import pandas as pd

import tools.translate as tr
import tools.TetradSearch as search
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.test as tt
import edu.cmu.tetrad.util as util
import edu.cmu.tetrad.algcomparison.independence as agind
import java.util as ju

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

_search = search.TetradSearch(data)
alpha_ = 0.01

# We are giving the option to use Causal Leearn's KCI test for the Markov Checker. In order to do this, we need to
# wrap the KCI test in a JPype object so that Tetrad can use it, and we need also to wrap this test as an
# IndependenceWrapper using JPype as well. This is verbose, but if it works, the functionality can be wrapped up nicely.

@JImplements(ts.IndependenceTest)
class KciWrapper:
    def __init__(self, df, alpha=alpha_):
        self.df = df
        self.data = df.values
        self.alpha = alpha
        self.kci_obj = CIT(self.data, "kci")

        self.variables = ju.ArrayList()
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

    @JOverride
    def getAlpha(self, *args):
        return self.alpha


@JImplements(agind.IndependenceWrapper)
class WrappedClKci:

    def __init__(self, df, alpha=alpha_):
        self.df = df
        self.alpha = alpha

    @JOverride
    def getTest(self, *args):
        # pandas = tr.tetrad_data_to_pandas(args[0])
        return KciWrapper(self.df)

    @JOverride
    def getDescription(self):
        return "Wrapped CL KCI"

    @JOverride
    def getDataType(self):
        return td.DataType.Continuous

    @JOverride
    def getParameters(self):
        return util.ArrayList()


# Now we need to choose which test to use for the Markov checker--either Fisher Z or WrappedClKci. We will use
# WrappedClKci in this example.

# Uncomment this line to use Fisher Z
# _search.use_fisher_z()

# Uncomment this line to use WrappedClKci
_search.use_test(WrappedClKci(data))

# Note that we have added an option to control whether parallelism is used in the Markov Checker, as we are not
# sure whether the Markov Checker is thread-safe when using the WrappedClKci test. We will test this in the future.
ad_ind, ad_dep, bin_indep, bin_dep, frac_dep_ind, frac_dep_dep, num_tests_ind, num_tests_dep, mc = _search.markov_check(
    cpdag, parallelized=True)

print(f"AD p-value Indep = {ad_ind:5.4} Dep = {ad_dep:5.4}")
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
