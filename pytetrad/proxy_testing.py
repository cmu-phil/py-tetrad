
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
import numpy as np

import pytetrad.tools.translate as tr

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.score as score

# Can use this as a template for defining scores in Python for use with
# Java Tetrad algorithms.
@JImplements(score.Score)
class Bsls:
    def __init__(self, df):
        self.df = df
        self.n, self.p = df.shape
        self.corr = df.corr().values
        self.penalty = 2 * np.log(self.n) / self.n
        self.variables = util.ArrayList()
        self.variable_map = {}
        for col in df.columns:
            col = str(col)
            variable = td.ContinuousVariable(col)
            self.variables.add(variable)
            self.variable_map[col] = variable


    @JOverride
    def localScore(self, *args):
        if len(args) == 1: return 0
        elif isinstance(args[1], int): S = [args[1]]
        else: S = list(args[1])

        score = -len(S) * self.penalty
        score += np.linalg.slogdet(self.corr[np.ix_(S, S)])[1]
        S.append(args[0])
        score -= np.linalg.slogdet(self.corr[np.ix_(S, S)])[1]

        return score

    @JOverride
    def localScoreDiff(self, *args):
        node = args[0]
        if len(args) == 2: parents = []
        else: parents = list(args[2])

        diff = -self.localScore(node, parents)
        parents.append(args[1])
        diff += self.localScore(node, parents)

        return diff 
    
    @JOverride
    def getVariables(self):
        return self.variables
    
    @JOverride
    def getSampleSize(self):
        return self.n

    @JOverride
    def toString(self):
        return "Bryan's Super Lame Score"

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

score_ = Bsls(df)

graph = ts.Fges(score_).search()
print('FGES w/ BSLS', graph)

data = tr.pandas_data_to_tetrad(df)
score = score.SemBicScore(data, True)
score.setPenaltyDiscount(1)
score.setStructurePrior(0)

graph = ts.Fges(score).search()
print('FGES w/ SEM-BIC', graph)