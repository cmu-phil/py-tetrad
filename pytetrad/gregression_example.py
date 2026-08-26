## Estimating total causal effects from a learned CPDAG with G-regression (Guo and Perkovic, 2022).
##
## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad
##
## 1. Simulate data from a random linear SEM with known coefficients, so true total effects are available.
## 2. Learn a CPDAG with BOSS.
## 3. For a handful of (treatment, outcome) pairs, ask whether the effect is identified from the CPDAG and,
##    if so, estimate it with a bootstrap standard error; compare with the truth.
## 4. Add one true orientation as background knowledge (giving an MPDAG) and show that more effects become
##    identified, without changing the estimates that were identified already.

import numpy as np
import pandas as pd

import pytetrad.tools.TetradSearch as ts
import pytetrad.tools.translate as tr
import pytetrad.tools.gregression as gr

import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.sem as sem
import edu.cmu.tetrad.util as tu

# ----------------------------------------------------------------------------- 1. simulate

num_vars, num_edges, n, seed = 12, 16, 5000, 20260826

tu.RandomUtil.getInstance().setSeed(seed)
dag = tg.RandomGraph.randomDag(num_vars, 0, num_edges, 100, 100, 100, False)
im = sem.SemIm(sem.SemPm(dag))
D = im.simulateData(n, False)
df = tr.tetrad_data_to_pandas(D)
df = df.astype({c: "float64" for c in df.columns})
names = [str(v) for v in D.getVariableNames()]

# Total effects implied by the true coefficient matrix. Gamma[i, j] is the coefficient on i -> j.
# Under do(A), edges into A are cut; the effect of a on Y is then entry (a, Y) of (I - Gamma_cut)^-1.
Gamma = tr.tetrad_matrix_to_numpy(im.getEdgeCoef())


def true_effect(treatments, outcome):
    idx = {v: i for i, v in enumerate(names)}
    G = Gamma.copy()
    for a in treatments:
        G[:, idx[a]] = 0.0
    T = np.linalg.inv(np.eye(len(names)) - G)
    return pd.Series([T[idx[a], idx[outcome]] for a in treatments], index=treatments, name=outcome)


print("True DAG:", dag)

# ----------------------------------------------------------------------------- 2. learn a CPDAG

search = ts.TetradSearch(df)
search.use_sem_bic(penalty_discount=2)
search.run_boss()
cpdag = search.get_java()
print("\nBOSS CPDAG:", cpdag)

est = search.get_gregression()
print("\nBuckets (undirected components, in causal order):", est.buckets())

# ----------------------------------------------------------------------------- 3. estimate effects

# Pick outcomes with several ancestors so the effects are interesting; pair each with one or two ancestors.
rng = np.random.default_rng(seed)
cases = []
for y in dag.getNodes():
    anc = sorted(str(a) for a in dag.paths().getAncestors(y) if a != y)
    if len(anc) < 2:
        continue
    for k in (1, 2):
        cases.append((sorted(rng.choice(anc, size=k, replace=False).tolist()), str(y.getName())))
    if len(cases) >= 10:
        break


def report(estimator, label):
    print(f"\n--- {label} ---")
    print(f"{'treatments':<14}{'outcome':<8}{'identified':<12}{'estimate':<12}{'boot SE':<10}{'truth':<10}")
    for A, Y in cases:
        truth = true_effect(A, Y)
        if estimator.is_identified(A, Y):
            b = estimator.bootstrap(A, Y, num_bootstraps=100, seed=seed)
            for a in A:
                print(f"{','.join(A):<14}{Y:<8}{'yes':<12}{b['effect'][a]:<12.4f}{b['se'][a]:<10.4f}{truth[a]:<10.4f}")
        else:
            for a in A:
                print(f"{','.join(A):<14}{Y:<8}{'no':<12}{'':<12}{'':<10}{truth[a]:<10.4f}")


report(est, "From the CPDAG")

# ----------------------------------------------------------------------------- 4. add background knowledge

# Choose an undirected edge whose orientation would help: one touching a treatment of an unidentified effect,
# if there is one, otherwise just the first undirected edge. Then tell the estimator its true direction.
undirected = [e for e in cpdag.getEdges() if tg.Edges.isUndirectedEdge(e)]
blocked = {a for A, Y in cases if not est.is_identified(A, Y) for a in A}
undirected.sort(key=lambda e: 0 if {str(e.getNode1().getName()), str(e.getNode2().getName())} & blocked else 1)
if undirected:
    e = undirected[0]
    x, z = str(e.getNode1().getName()), str(e.getNode2().getName())
    tail, head = (x, z) if dag.isParentOf(dag.getNode(x), dag.getNode(z)) else (z, x)
    print(f"\nAdding background knowledge: {tail} --> {head}")

    mpdag = gr.orient_with_knowledge(cpdag, required=[(tail, head)])
    print("MPDAG after Meek closure:", mpdag)
    print("Undirected edges: CPDAG", len(undirected), "-> MPDAG",
          sum(1 for f in mpdag.getEdges() if tg.Edges.isUndirectedEdge(f)))

    report(gr.GRegression(mpdag, df), "From the MPDAG (CPDAG + one known orientation)")
else:
    print("\nThe CPDAG is fully oriented; nothing to add.")

## A note on reading the output. Estimates agree with the truth to within about two bootstrap standard
## errors, except when the search has dropped a weak edge: the estimator then returns exactly 0 with SE 0,
## because in the graph it was handed there is no directed path at all. G-regression is exact for the graph
## it is given; it cannot repair the graph. Report effects together with the bootstrap edge frequencies of the
## edges their identification and value depend on.
