"""Sweep pd x {fges, boss}, run Vertex Repair on each candidate, re-check Markov.
Documents which (algorithm, pd, repair) cells reach Markov adequacy on Auto MPG."""
import sys
import jpype
import jpype.imports

jpype.startJVM(classpath=["/tmp/work/tetrad-current.jar"], convertStrings=False)

import pandas as pd
sys.path.insert(0, "/tmp/pytetrad")
import pytetrad.tools.TetradSearch as ts_mod
import pytetrad.tools.translate as tr
import edu.cmu.tetrad.search as tsearch
import edu.cmu.tetrad.search.test as ttest

df = pd.read_csv("/tmp/pytetrad/pytetrad/resources/auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
for col in df.columns:
    df[col] = df[col].astype(float)
df["origin"] = df["origin"].astype(int)

data_java = tr.pandas_data_to_tetrad(df)
CST = tsearch.ConditioningSetType.ORDERED_LOCAL_MARKOV_PROPERTY

def check(search, graph):
    r = search.markov_check(graph, condition_set_type=CST)
    return r[0], r[7], r[8], r[9]   # ad_ind, frac_dep_dep, n_ind, n_dep

rows = []
for alg in ["fges", "boss"]:
    for pd_ in [1.0, 2.0, 4.0]:
        search = ts_mod.TetradSearch(df)
        search.use_degenerate_gaussian_score(penalty_discount=pd_)
        search.use_degenerate_gaussian_test(alpha=0.01, use_for_mc=True)
        if alg == "fges":
            search.run_fges()
        else:
            search.run_boss()
        g = search.get_java()

        ad0, dep0, ni0, nd0 = check(search, g)

        test = ttest.IndTestDegenerateGaussianLrt(data_java)
        test.setAlpha(0.01)
        repair = tsearch.VertexRepairSearch(g, test, CST)
        repaired = repair.search()
        ad1, dep1, ni1, nd1 = check(search, repaired)

        rows.append((alg, pd_, g.getNumEdges(), ad0, repaired.getNumEdges(), ad1))
        print(f"{alg} pd={pd_}: edges {g.getNumEdges()} ad_ind {ad0:.4f}  "
              f"--repair--> edges {repaired.getNumEdges()} ad_ind {ad1:.4f}"
              f"{'   <-- MARKOV ADEQUATE' if ad1 > 0.05 else ''}")
        if ad1 > 0.05:
            print("  repaired graph:")
            for e in repaired.getEdges():
                print("   ", e)

print("\nalg  pd  edges  ad_pre   edges'  ad_post")
for r in rows:
    print(f"{r[0]:4} {r[1]:3} {r[2]:5}  {r[3]:.4f}  {r[4]:5}  {r[5]:.4f}")
