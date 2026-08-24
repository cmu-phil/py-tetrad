## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd

import pytetrad.tools.TetradSearch as search

### Pooling several data sets that share a causal structure but not necessarily the same
### parameters. This is the general replacement for the old dedicated IMaGES algorithm: pooling
### is now a property of the search (add_data_set + set_pool_data_sets) rather than a separate
### algorithm, so any score-based search pools as IMaGES did (the score is summed across data
### sets), and any test-based search pools by combining per-data-set p-values (Fisher's method by
### default, or Tippett's; see set_pooled_test_method).
###
### A real use case is several subjects, sessions, or regions with the same variables. For a
### demo, we split one dataset's rows into three non-overlapping chunks and treat those as if
### they were separate data sets — the pooled search should recover essentially the same
### structure as running on the full data at once, since a real split of one dataset is the
### simplest sanity check.

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

third = len(df) // 3
df1 = df.iloc[:third].reset_index(drop=True)
df2 = df.iloc[third:2 * third].reset_index(drop=True)
df3 = df.iloc[2 * third:].reset_index(drop=True)

print("Score-based pooling (IMaGES-equivalent): BOSS + SEM-BIC, pooled over three data sets")
pooled_score = search.TetradSearch(df1)
pooled_score.use_sem_bic(penalty_discount=2)
pooled_score.add_data_set(df2)
pooled_score.add_data_set(df3)
pooled_score.set_pool_data_sets(True)
pooled_score.run_boss()
print(pooled_score.get_java())

print("Test-based pooling: PC + Fisher Z, pooled by Fisher's method (the default)")
pooled_test = search.TetradSearch(df1)
pooled_test.use_fisher_z(alpha=0.01)
pooled_test.add_data_set(df2)
pooled_test.add_data_set(df3)
pooled_test.set_pool_data_sets(True)
pooled_test.run_pc()
print(pooled_test.get_java())

print("Same, but combined by Tippett's method (min p, Sidak-adjusted) -- more powerful when a")
print("dependence is present in only some of the pooled data sets, at a small cost in power when")
print("it is present in all of them:")
pooled_test.set_pooled_test_method("tippett")
pooled_test.run_pc()
print(pooled_test.get_java())
