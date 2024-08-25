# This module wraps the KCI test from causal-learn in a JPype object so that Tetrad can use it.
# We are not assuming in this repository that causal-learn is installed, as we don't want to
# have the dependency in our code (since some people can't have it there--it has dependencies
# that are unhelpful in certain circumstances). So if you want to use the KCI test from causal-learn,
# you will need to install causal-learn yourself. (See the docs for causal-learn for installation
# instructions.)
#
# To use WrappedClKci as a test in py-tetrad, you can do the following:
# import tools/WrappedClKci as wc
# ... load data into a pandas DataFrame df ...
# test = wc.WrappedClKci(df, alpha=0.01)
#
# This test will implement the IndependenceWrapper interface in Tetrad. For a test that implements the
# IndependenceTest interface in Tetrad, use KciWrapper instead, in this module.
#
# jdramsey 2024-08-24

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

import tools.translate as tr
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.test as tt
import edu.cmu.tetrad.util as util
import edu.cmu.tetrad.algcomparison.independence as agind
import java.util as ju

@JImplements(ts.IndependenceTest)
class KciWrapper:
    def __init__(self, df, alpha=0.01):
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
    def __init__(self, df, alpha=0.01):
        self.df = df
        self.alpha = alpha

    @JOverride
    def getTest(self, *args):
        return KciWrapper(self.df, alpha=self.alpha)

    @JOverride
    def getDescription(self):
        return "Wrapped CL KCI"

    @JOverride
    def getDataType(self):
        return td.DataType.Continuous

    @JOverride
    def getParameters(self):
        return util.ArrayList()
