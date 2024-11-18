
from jpype import JImplements, JOverride
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

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.score as score

try:
    from causallearn.score.LocalScoreFunction import local_score_marginal_general
    from causallearn.score.LocalScoreFunction import local_score_cv_general
except ImportError as e:
    print('Could not import a causal-learn module: ', e)


# Can use this as a template for defining scores in Python for use with
# Java Tetrad algorithms.
@JImplements(score.Score)
class Bgs:
    def __init__(self, df):
        self.df = df
        self.data = df.values
        self.parameters = {"kfold": 10, "lambda": 0.01}

        # pick a score: bug in marginal_general?
        # self.score = local_score_marginal_general
        self.score = local_score_cv_general

        # these scores are expensive, so caching seems pertinent...
        self.cache = {}

        self.variables = util.ArrayList()
        self.variable_map = {}
        for col in df.columns:
            col = str(col)
            variable = td.ContinuousVariable(col)
            self.variables.add(variable)
            self.variable_map[col] = variable

    # camelCase is java convention; mathcing that...
    def setParameters(self, parameters):
        self.paramaters = parameters

    @JOverride
    def localScore(self, *args):
        Xi = args[0] 
        if len(args) == 1: PAi = []
        elif isinstance(args[1], int): PAi = [args[1]]
        else: PAi = list(args[1])

        key = (Xi, *sorted(PAi))
        if key not in self.cache:
            self.cache[key] = self.score(self.data, Xi, PAi, self.parameters)
 
        # for debugging...
        # print(key, self.cache[key])
        return self.cache[key]

    @JOverride
    def localScoreDiff(self, *args):
        Xi = args[0]
        if len(args) == 2: PAi = []
        else: PAi = list(args[2])

        diff = -self.localScore(Xi, PAi)
        PAi.append(args[1])
        diff += self.localScore(Xi, PAi)

        return diff 
    
    @JOverride
    def getVariables(self):
        return self.variables
    
    @JOverride
    def getSampleSize(self):
        return self.n

    @JOverride
    def toString(self):
        return "Biwei's General Score"

    @JOverride
    def getVariable(self, targetName):
        if targetName in self.variable_map: 
            return self.variable_map[targetName]
        return None

    @JOverride
    def isEffectEdge(self, bump):
        return False

    @JOverride
    def getMaxDegree(self):
        return 1000

    @JOverride
    def defaultScore(self):
        return self


df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

# subsampling bc slow...
score = Bgs(df.sample(n=500))

graph = ts.Fges(score).search()
print('FGES w/ BGS', graph)

data = tr.pandas_data_to_tetrad(df)
score = ts.SemBicScore(data, True)
score.setPenaltyDiscount(1)
score.setStructurePrior(0)

graph = ts.Fges(score).search()
print('FGES w/ SEM-BIC', graph)