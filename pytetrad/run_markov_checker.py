import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import pandas as pd

# Will wrap the Markov Checker in a nicer Python class at some point. -JR

import tools.translate as tr
import tools.TetradSearch as search
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.ConditioningSetType as cst
import edu.cmu.tetrad.algcomparison.independence as ind_
from edu.cmu.tetrad.util import Params, Parameters


data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

## Make a TetradSearch instance to run searches against. This helps to organize
## the use of Tetrad search algorithms and hides the JPype code for those who
## don't want to deal with it.
search = search.TetradSearch(data)
search.set_verbose(False)

## Pick the score to use, in this case a continuous linear, Gaussian score.
search.use_sem_bic()
search.use_fisher_z(alpha=0.05)

## Run various algorithms and print their results. For now (for compability with R)
print('BOSS')
search.run_boss(num_starts=1, use_bes=True, time_lag=0, use_data_order=True)
print(search.get_string())
dag=search.get_dag_java()
print(dag)

params = Parameters()
params.set(Params.ALPHA, 0.01)
_test = ind_.FisherZ().getTest(tr.pandas_data_to_tetrad(data), params)

mc = ts.MarkovCheck(dag, _test, cst.LOCAL_MARKOV)
mc.generateResults()    
p_ks_indep = mc.getKsPValue(True)
print("ks p-value Indep = ", p_ks_indep)

fd_indep = mc.getFractionDependent(True)
fd_dep = mc.getFractionDependent(False)

print("Fraction dependent for Indep = ", fd_indep, " fraction dependent Dep = ", fd_dep)