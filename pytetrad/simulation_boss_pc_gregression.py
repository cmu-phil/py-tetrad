"""
Reproduces the October 11 simulation from start to finish:

  1. A connected random DAG over X1..X10: no latents, 15 edges, maximum
     indegree 3, maximum outdegree 3 (graph seed 42).
  2. A linear Gaussian SEM on that DAG: edge coefficients uniform on -1 to 1,
     error variances uniform on 1 to 3 (parameter seed 2026). 1,000 samples.
  3. BOSS (SEM BIC, penalty discount 2) and PC (Fisher Z, alpha 0.01,
     MAX_P collider orientation), each scored against the true CPDAG.
  4. G-regression for every ordered pair of distinct variables, using the
     BOSS graph, the PC graph, and the true CPDAG, compared with the true
     total effects.

Everything calls Tetrad directly through JPype, using the tetrad-current.jar
that ships with py-tetrad, so the numbers should match the earlier run.

Run it from IntelliJ, or from Terminal with the py-tetrad .venv active:
    python simulation_boss_pc_gregression.py

Output files go into a folder called "sim_output" next to this script.
Requires JPype1, numpy, and pandas, and JAVA_HOME pointing at JDK 21+.
"""

import os

import jpype
import jpype.imports
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
NUM_VARS = 10
NUM_EDGES = 15
MAX_DEGREE = 6
MAX_INDEGREE = 3
MAX_OUTDEGREE = 3
GRAPH_SEED = 42

COEF_LOW, COEF_HIGH = 0.0, 1.0  # magnitude range; random sign gives -1 to 1
VAR_LOW, VAR_HIGH = 1.0, 3.0
PARAM_SEED = 2026
SAMPLE_SIZE = 1000

BOSS_PENALTY_DISCOUNT = 2.0
PC_ALPHA = 0.01
NUM_BOOTSTRAPS = 200

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "sim_output")
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Start the JVM with py-tetrad's jar
# ---------------------------------------------------------------------------
def find_jar():
    """Use the jar from the installed pytetrad package, or one next to this script."""
    try:
        import importlib.resources as resources
        jar = str(resources.files("pytetrad").joinpath("resources", "tetrad-current.jar"))
        if os.path.exists(jar):
            return jar
    except ModuleNotFoundError:
        pass
    jar = os.path.join(HERE, "tetrad-current.jar")
    if os.path.exists(jar):
        return jar
    raise FileNotFoundError(
        "Could not find tetrad-current.jar. Either run 'pip install -e .' in your "
        "py-tetrad folder, or copy pytetrad/resources/tetrad-current.jar next to this script.")


if not jpype.isJVMStarted():
    jpype.startJVM("-Xmx4g", classpath=[find_jar()])

# Java imports (only possible after the JVM has started)
import java.io as jio
import java.util as jutil
from edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag import Boss as BossAlg
from edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag import Pc as PcAlg
from edu.cmu.tetrad.algcomparison.independence import FisherZ
from edu.cmu.tetrad.algcomparison.score import SemBicScore
from edu.cmu.tetrad.algcomparison.statistic import (
    AdjacencyPrecision, AdjacencyRecall, ArrowheadPrecision, ArrowheadRecall,
    StructuralHammingDistance)
from edu.cmu.tetrad.data import SimpleDataLoader
from edu.cmu.tetrad.data import CovarianceMatrix
from edu.cmu.tetrad.graph import GraphSaveLoadUtils, GraphTransforms, GraphUtils, RandomGraph
from edu.cmu.tetrad.search import GRegression
from edu.cmu.tetrad.sem import SemIm, SemPm
from edu.cmu.tetrad.util import Parameters, Params, RandomUtil
from edu.pitt.dbmi.data.reader import Delimiter

NAMES = [f"X{i}" for i in range(1, NUM_VARS + 1)]


def edge_key(edge):
    return int(str(edge.getNode1().getName())[1:]), int(str(edge.getNode2().getName())[1:])


def sorted_edges(graph):
    return sorted(graph.getEdges(), key=edge_key)


def print_graph_vs_truth(graph, truth):
    for e in sorted_edges(graph):
        t = truth.getEdge(e.getNode1(), e.getNode2())
        note = "" if (t is not None and t.equals(e)) else (
            "   [not in truth]" if t is None else f"   [truth: {t}]")
        print(f"  {e}{note}")
    for t in sorted_edges(truth):
        if not graph.isAdjacentTo(t.getNode1(), t.getNode2()):
            print(f"  MISSING {t}")


def print_stats(dag, cpdag, est, data, params):
    stats = [("Adj prec", AdjacencyPrecision()), ("Adj rec", AdjacencyRecall()),
             ("Arrow prec", ArrowheadPrecision()), ("Arrow rec", ArrowheadRecall()),
             ("SHD", StructuralHammingDistance())]
    print("  " + ", ".join(f"{name} {float(s.getValue(dag, cpdag, est, data, params)):.3f}"
                           for name, s in stats))


# ---------------------------------------------------------------------------
# 1. Random DAG
# ---------------------------------------------------------------------------
dag = RandomGraph.randomDag(NUM_VARS, 0, NUM_EDGES, MAX_DEGREE, MAX_INDEGREE,
                            MAX_OUTDEGREE, True, jpype.JLong(GRAPH_SEED))
print("1. True DAG")
for e in sorted_edges(dag):
    print(f"  {e}")
GraphSaveLoadUtils.saveGraph(dag, jio.File(os.path.join(OUT_DIR, "true_graph.txt")), False)

# ---------------------------------------------------------------------------
# 2. Linear Gaussian SEM and data
# ---------------------------------------------------------------------------
RandomUtil.getInstance().setSeed(jpype.JLong(PARAM_SEED))
sim_params = Parameters()
sim_params.set(Params.COEF_LOW, COEF_LOW)
sim_params.set(Params.COEF_HIGH, COEF_HIGH)
sim_params.set(Params.COEF_SYMMETRIC, True)
sim_params.set(Params.VAR_LOW, VAR_LOW)
sim_params.set(Params.VAR_HIGH, VAR_HIGH)

sem_im = SemIm(SemPm(dag), sim_params)
sim_data = sem_im.simulateData(SAMPLE_SIZE, False)

# Coefficient matrix B, with B[i, j] the coefficient on Xi -> Xj.
B = np.zeros((NUM_VARS, NUM_VARS))
print("\n2. True parameters")
for e in sorted_edges(dag):
    i, j = edge_key(e)
    B[i - 1, j - 1] = float(sem_im.getEdgeCoef(e))
    print(f"  {e}   coefficient {B[i - 1, j - 1]: .4f}")
for node in dag.getNodes():
    print(f"  {node}   error variance {float(sem_im.getErrVar(node)):.4f}")

# True total effects: entry (i, j) of (I - B)^-1 is the effect of Xi on Xj.
TRUE_EFFECTS = np.linalg.inv(np.eye(NUM_VARS) - B)

# Save the data to six decimal places, then load it back, exactly as before.
cols = [str(v.getName()) for v in sim_data.getVariables()]
rows = [[float(sim_data.getDouble(r, c)) for c in range(sim_data.getNumColumns())]
        for r in range(sim_data.getNumRows())]
data_file = os.path.join(OUT_DIR, "sim_data_n1000.txt")
pd.DataFrame(rows, columns=cols).to_csv(data_file, sep="\t", index=False, float_format="%.6f")
data = SimpleDataLoader.loadContinuousData(jio.File(data_file), "//", jpype.JChar('"'), "*",
                                           True, Delimiter.TAB, False)
print(f"  Saved {SAMPLE_SIZE} rows to {data_file}")

# Put the true graphs on the data's variable objects so everything compares by node.
dag = GraphUtils.replaceNodes(dag, data.getVariables())
true_cpdag = GraphTransforms.dagToCpdag(dag)

# ---------------------------------------------------------------------------
# 3. BOSS and PC
# ---------------------------------------------------------------------------
search_params = Parameters()
search_params.set(Params.PENALTY_DISCOUNT, BOSS_PENALTY_DISCOUNT)
search_params.set(Params.SEM_BIC_STRUCTURE_PRIOR, 0)
search_params.set(Params.SEM_BIC_RULE, 1)
search_params.set(Params.USE_BES, False)
search_params.set(Params.NUM_STARTS, 1)
search_params.set(Params.USE_DATA_ORDER, True)
search_params.set(Params.OUTPUT_CPDAG, True)
search_params.set(Params.ALPHA, PC_ALPHA)
search_params.set(Params.SINGULARITY_LAMBDA, 0.0)
search_params.set(Params.DEPTH, -1)
search_params.set(Params.STABLE_FAS, True)
search_params.set(Params.ALLOW_BIDIRECTED, False)
search_params.set(Params.COLLIDER_ORIENTATION_STYLE, 3)  # 3 = MAX_P, py-tetrad's default
search_params.set(Params.FDR_Q, 0.0)
search_params.set(Params.TIME_LAG, 0)
search_params.set(Params.VERBOSE, False)

boss_graph = GraphUtils.replaceNodes(BossAlg(SemBicScore()).search(data, search_params),
                                     data.getVariables())
pc_graph = GraphUtils.replaceNodes(PcAlg(FisherZ()).search(data, search_params),
                                   data.getVariables())

print(f"\n3a. BOSS (SEM BIC, penalty discount {BOSS_PENALTY_DISCOUNT}) vs true CPDAG")
print_graph_vs_truth(boss_graph, true_cpdag)
print_stats(dag, true_cpdag, boss_graph, data, search_params)

print(f"\n3b. PC (Fisher Z, alpha {PC_ALPHA}, MAX_P colliders) vs true CPDAG")
print_graph_vs_truth(pc_graph, true_cpdag)
print_stats(dag, true_cpdag, pc_graph, data, search_params)

# ---------------------------------------------------------------------------
# 4. G-regression on every ordered pair, for each graph
# ---------------------------------------------------------------------------
cov = CovarianceMatrix(data)
graphs = {"true_cpdag": true_cpdag, "boss": boss_graph, "pc": pc_graph}
estimators = {}
for label, g in graphs.items():
    problem = GRegression.mpdagProblem(g)
    if problem is not None:
        raise ValueError(f"The {label} graph is not a valid MPDAG: {problem}")
    estimators[label] = GRegression(g, cov)


def estimate(label, x_name, y_name, pair_seed):
    """Returns (identified, estimate, bootstrap SE, witness path)."""
    g, est = graphs[label], estimators[label]
    x, y = data.getVariable(x_name), data.getVariable(y_name)
    treatments = jutil.ArrayList()
    treatments.add(x)
    if not est.isIdentified(treatments, y):
        witness = est.nonIdentificationWitness(treatments, y)
        return False, None, None, str(GRegression.pathString(g, witness))
    RandomUtil.getInstance().setSeed(jpype.JLong(pair_seed))
    result = GRegression.bootstrap(g, data, treatments, y, NUM_BOOTSTRAPS)
    return True, float(result.effect()[0]), float(result.standardErrors()[0]), ""


records = []
for i, x in enumerate(NAMES, start=1):
    for j, y in enumerate(NAMES, start=1):
        if i == j:
            continue
        row = {"treatment": x, "outcome": y, "true_effect": TRUE_EFFECTS[i - 1, j - 1]}
        for label in graphs:
            ident, value, se, witness = estimate(label, x, y, PARAM_SEED + 100 * i + j)
            row[f"id_{label}"] = "yes" if ident else "no"
            row[f"est_{label}"] = value
            row[f"se_{label}"] = se
            row[f"blocking_path_{label}"] = witness
        records.append(row)

results = pd.DataFrame(records)
results_file = os.path.join(OUT_DIR, "gregression_all_pairs.csv")
results.to_csv(results_file, index=False, float_format="%.4f")


def compare(label):
    """Summarizes how a learned graph's g-regression differs from the true CPDAG's."""
    t_id, l_id = results["id_true_cpdag"] == "yes", results[f"id_{label}"] == "yes"
    both = results[t_id & l_id]
    differ = both[(both[f"est_{label}"] - both["est_true_cpdag"]).abs() > 1e-9]
    print(f"\n4. G-regression: {label.upper()} graph vs true CPDAG")
    print(f"  Identified by both: {len(both)} (estimates differ in {len(differ)})")
    print(f"  Identified only from the true CPDAG: {int((t_id & ~l_id).sum())}")
    print(f"  Identified only from the {label.upper()} graph: {int((~t_id & l_id).sum())}")
    print(f"  Identified by neither: {int((~t_id & ~l_id).sum())}")
    for _, r in differ.iterrows():
        print(f"    {r.treatment} on {r.outcome}: true CPDAG {r.est_true_cpdag:.4f}, "
              f"{label.upper()} {r[f'est_{label}']:.4f}, truth {r.true_effect:.4f}")


compare("boss")
compare("pc")

nonzero = results[(results["id_true_cpdag"] == "yes") & (results["true_effect"].abs() > 1e-12)]
print("\n  Nonzero identified effects (true CPDAG): estimate, bootstrap SE, truth")
for _, r in nonzero.iterrows():
    print(f"    {r.treatment} on {r.outcome}: {r.est_true_cpdag: .4f}  "
          f"{r.se_true_cpdag:.4f}  {r.true_effect: .4f}")

print(f"\nAll 90 pairs saved to {results_file}")
