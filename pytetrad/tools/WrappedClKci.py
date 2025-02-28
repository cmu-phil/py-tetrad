# This module wraps the KCI test from causal-learn in a JPype object so that Tetrad can use it.
# We are not assuming in this repository that causal-learn is installed, as we don't want to
# have the dependency in our code (since some people can't have it there--it has dependencies
# that are unhelpful in certain circumstances). So if you want to use the KCI test from causal-learn,
# you will need to install causal-learn yourself. (See the docs for causal-learn for installation
# instructions.)
#
# To use WrappedClKci as a test in py-tetrad, you can do the following:
# import pytetrad.tools/WrappedClKci as wc
# ... load data into a pandas DataFrame df ...
# test = wc.WrappedClKci(df, alpha=0.01)
#
# This test will implement the IndependenceWrapper interface in Tetrad. For a test that implements the
# IndependenceTest interface in Tetrad, use KciWrapper instead, in this module.
#
# jdramsey 2024-08-24

import time as tm

import jpype.imports
from jpype import JImplements, JOverride

import importlib.resources as importlib_resources

jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

try:
    from causallearn.utils.cit import CIT
    from causallearn.search.ConstraintBased.PC import pc
    from causallearn.utils.cit import kci
except ImportError as e:
    print('Could not import a causal-learn module: ', e)

import pytetrad.tools.translate as tr
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.test as tt
import edu.cmu.tetrad.util as util
import edu.cmu.tetrad.algcomparison.independence as agind
import java.util as ju

# This is the wrapper for the KCI test from causal-learn. It implements the IndependenceTest interface in Tetrad.
# The KCI test is a kernel-based independence test that can be used in Tetrad.
#
# The following parameters can be passed to the KCI test:
#
#         kernelX: kernel function for input data x
#             'Gaussian': Gaussian kernel
#             'Polynomial': Polynomial kernel
#             'Linear': Linear kernel
#         kernelY: kernel function for input data y
#         est_width: set kernel width for Gaussian kernels
#             'empirical': set kernel width using empirical rules
#             'median': set kernel width using the median trick
#             'manual': set by users
#         null_ss: sample size in simulating the null distribution
#         approx: whether to use gamma approximation (default=True)
#         polyd: polynomial kernel degrees (default=1)
#         kwidthx: kernel width for data x (standard deviation sigma)
#         kwidthy: kernel width for data y (standard deviation sigma)
#
@JImplements(ts.IndependenceTest)
class KciWrapper:
    def __init__(self, df, alpha=0.01, start_time=-1, timeout=-1, **kwargs):
        self.df = df
        self.data = df.values
        self.alpha = alpha
        self.kci_obj = CIT(self.data, "kci", **kwargs)

        self.start_time = start_time
        self.timeout = timeout

        self.variables = ju.ArrayList()
        self.variable_map = {}
        self.reverse_variable_map = {}

        for col in df.columns:
            variable = td.ContinuousVariable(str(col))
            self.variables.add(variable)
            self.variable_map[col] = variable
            self.reverse_variable_map[variable] = df.columns.get_loc(col)

    @JOverride
    def checkIndependence(self, *args):
        if self.start_time != -1 and self.timeout != -1 and tm.time() > self.start_time + self.timeout:
            raise Exception("Timeout")

        x = args[0]
        y = args[1]
        s = args[2]
        fact = tg.IndependenceFact(x, y, s)

        # Convert x, y, s to indices using the reverse map
        X = self.reverse_variable_map[x]
        Y = self.reverse_variable_map[y]
        S = [self.reverse_variable_map[si] for si in s]

        pValue = self.kci_obj(X, Y, S)

        # print("p = " + pValue)
        print("Found " + str(pValue) + " for " + str(x) + " and " + str(y) + " given " + str(s))

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
    def __init__(self, df, alpha=0.01, **kwargs):
        self.df = df
        self.alpha = alpha
        self.kwargs = kwargs

    @JOverride
    def getTest(self, *args):
        return KciWrapper(self.df, **self.kwargs)

    @JOverride
    def getDescription(self):
        return "Wrapped CL KCI"

    @JOverride
    def getDataType(self):
        return td.DataType.Continuous

    @JOverride
    def getParameters(self):
        return util.ArrayList()
