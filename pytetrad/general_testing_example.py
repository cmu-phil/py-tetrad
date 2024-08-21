
from jpype import JImplements, JOverride
import jpype.imports

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
except ImportError as e:
    print('Could not import a causal-learn module: ', e)

@JImplements(ts.IndependenceTest)
class KciWrapper:
    def __init__(self, df, alpha = 0.01):
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

    # IndependenceResult checkIndependence(Node x, Node y, Set<Node> z);
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


df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

# subsampling bc slow...
test = KciWrapper(df.sample(n=500))

graph = ts.Pc(test).search()
print('PC w/ KciWrapper', graph)
