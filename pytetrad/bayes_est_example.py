# This script assumes that py-tetrad is installed and that you can run
# the other examples (e.g., run_discrete.py) successfully.
#
# Pipeline:
#   1. Load the (discretized) bridges dataset.
#   2. Run BOSS with a discrete score to get a CPDAG.
#   3. Pick a DAG in the CPDAG equivalence class.
#   4. Do Bayes estimation for that DAG.
#   5. Print the resulting BayesIm, i.e., the CPTs.

import pandas as pd
import pytetrad.tools.TetradSearch as ts
import pytetrad.tools.translate as translate

import edu.cmu.tetrad.graph as tgraph
import edu.cmu.tetrad.bayes as tbayes

# 1. Load data (same file you use in run_discrete.py)
data = pd.read_csv("resources/sample_discrete.txt", sep="\t")
# clean = data.replace("?", pd.NA).dropna()

# 2. Make a TetradSearch instance
search = ts.TetradSearch(data)
search.set_verbose(False)

# Use a discrete score; BDeu is the usual choice
search.use_bdeu(sample_prior=10.0, structure_prior=0.0)

# Run BOSS (this should produce a CPDAG)
search.run_boss()

print("=== BOSS CPDAG for bridges ===")
print(search.get_string())      # human-readable description of the CPDAG
print()

# 3. Pick a DAG in the CPDAG equivalence class.
dag = tgraph.GraphTransforms.dagFromCpdag(search.get_java())

print("=== Selected DAG in the CPDAG equivalence class ===")
print(dag)                          # or print(search.graph_to_string(dag))
print()

# 4. Do Bayes estimation on that DAG using the underlying discrete data.
#    Again, this is easiest if you hide JPype & Java details in a helper.
# bayes_im = search.estimate_discrete_bayes(dag)
bayes_pm = tbayes.BayesPm(dag)

box_data = translate.pandas_data_to_tetrad(data)   # BoxDataSet
bayes_im = tbayes.MlBayesEstimator(1).estimate(bayes_pm, box_data)

print("=== BayesIm (CPTs) for the selected DAG ===")
print(bayes_im)                     # BayesIm.__str__ already prints CPTs nicely
print()
