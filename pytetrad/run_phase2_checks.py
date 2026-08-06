"""End-to-end verification of pytetrad.tools.audit and pytetrad.tools.sweep against the
augmented jar. Run from the pytetrad/ directory."""

import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "..")

import pytetrad.tools.audit as au
import pytetrad.tools.sweep as sw
import pytetrad.tools.TetradSearch as ts

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("PASS", name)
    else:
        failed += 1
        print("FAIL", name, "\n ", detail)


rng = np.random.default_rng(42)
n = 500

# Simulated data with planted pathologies for the audit.
x1 = rng.normal(size=n)
x2 = 0.8 * x1 + rng.normal(size=n)
x3 = x2 + 0.01 * rng.normal(size=n)          # collinear/near-deterministic with x2
x4 = np.exp(rng.normal(size=n))              # non-Gaussian
year = rng.integers(70, 83, size=n)          # int column -> discrete, 13 levels

df_audit = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "x4": x4, "year": year})

# ---- audit ----
res = au.audit(df_audit)
check("audit.findings_df", set(res.findings.columns)
      == {"code", "severity", "variables", "values", "message"}, str(res.findings.columns))
check("audit.high_correlation", res.has("HIGH_CORRELATION"), res.report)
check("audit.near_determinism", res.has("NEAR_DETERMINISM_CONTINUOUS"), res.report)
check("audit.non_gaussian", res.has("NON_GAUSSIAN"), res.report)
check("audit.many_levels", res.has("DISCRETE_MANY_LEVELS"), res.report)
check("audit.report_str", "Data audit:" in res.report and str(res) == res.report, res.report[:80])
check("audit.json", res.json.count("{") == res.json.count("}") and '"findings":[' in res.json, "")

# int_as_cont flips the year column's treatment.
res2 = au.audit(df_audit, int_as_cont=True)
check("audit.int_as_cont", not res2.has("DISCRETE_MANY_LEVELS"), res2.report)

# Threshold kwargs take effect and unknown kwargs are rejected.
res3 = au.audit(df_audit, high_correlation=0.99999999, ad_alpha=1e-300)
check("audit.thresholds", not res3.has("NON_GAUSSIAN"), res3.report)
try:
    au.audit(df_audit, bogus_threshold=1)
    check("audit.unknown_kwarg", False, "no error raised")
except TypeError as e:
    check("audit.unknown_kwarg", "bogus_threshold" in str(e), str(e))

# Values map includes the threshold used.
hc = res.findings[res.findings.code == "HIGH_CORRELATION"].iloc[0]
check("audit.values_threshold", hc["values"].get("threshold") == 0.9, str(hc["values"]))

# ---- sweep ----
df_cont = df_audit[["x1", "x2", "x4"]].copy()
df_cont["x5"] = 0.5 * df_cont["x1"] + rng.normal(size=n)
df_cont["x6"] = 0.7 * df_cont["x5"] + rng.normal(size=n)

search = ts.TetradSearch(df_cont)
search.use_sem_bic()
search.use_fisher_z(alpha=0.01, use_for_mc=True)

report = sw.sweep(search, "boss", "penaltyDiscount", [1.0, 2.0, 4.0],
                  num_resamples=10, seed=42, verbose=False)

t = report.table
check("sweep.table_shape", len(t) == 3 and "instability" in t.columns and "ad_ind" in t.columns,
      str(t))
check("sweep.setting_col", list(t["penaltyDiscount"]) == [1, 2, 4], str(t))
check("sweep.instability_bounds", ((t.instability >= 0) & (t.instability <= 0.5)).all(), str(t))
check("sweep.monotone", t.num_edges.iloc[2] <= t.num_edges.iloc[0], str(t))
check("sweep.markdown", "| Setting |" in report.markdown, report.markdown)
check("sweep.json", report.json.count("{") == report.json.count("}"), "")
check("sweep.point_graph", "Graph Edges" in report.point_graph(0)
      or "-->" in report.point_graph(0) or "---" in report.point_graph(0), report.point_graph(0))
check("sweep.prob_graph", report.probability_graph(0) is not None, "")
check("sweep.markov_stats", report.markov_stats(0) is not None
      and report.markov_stats(0)["num_tests_ind"] >= 0, str(report.markov_stats(0)))

i_mc = report.select_by_markov_adequacy()
check("sweep.select_markov", i_mc is not None
      and t.ad_ind.iloc[i_mc] == t.ad_ind.max(), f"i={i_mc}\n{t}")

max_d = t.instability.max()
i_st = report.select_by_instability(max_d + 1e-9)
check("sweep.select_instability", i_st is not None
      and t.instability.iloc[i_st] == max_d, f"i={i_st}\n{t}")
check("sweep.select_most_stable", t.instability.iloc[report.select_most_stable()]
      == t.instability.min(), str(t))

# Two-parameter cross product.
report2 = sw.sweep(search, "fges", "penaltyDiscount", [1.0, 2.0], "faithfulnessAssumed",
                   [True, False], num_resamples=5, seed=7, markov_check=False)
check("sweep.two_param", len(report2.table) == 4
      and "faithfulnessAssumed" in report2.table.columns, str(report2.table))

# Missing MC test raises informatively.
search_no_mc = ts.TetradSearch(df_cont)
search_no_mc.use_sem_bic()
try:
    sw.sweep(search_no_mc, "boss", "penaltyDiscount", [1.0], num_resamples=0)
    check("sweep.mc_missing_raises", False, "no error raised")
except Exception as e:
    check("sweep.mc_missing_raises", "use_for_mc" in str(e), str(e))

# Knowledge flows through: forbidding an edge tier-wise removes x6 as a cause of x1.
search_k = ts.TetradSearch(df_cont)
search_k.use_sem_bic()
search_k.use_fisher_z(alpha=0.01, use_for_mc=True)
search_k.add_to_tier(0, "x1")
search_k.add_to_tier(1, "x5")
search_k.add_to_tier(1, "x6")
report_k = sw.sweep(search_k, "boss", "penaltyDiscount", [2.0], num_resamples=0)
g = report_k.point_graph(0)
check("sweep.knowledge", "x5 --> x1" not in g and "x6 --> x1" not in g, g)

# Unsupported algorithm raises.
try:
    sw.sweep(search, "lingam", "penaltyDiscount", [1.0])
    check("sweep.bad_alg", False, "no error raised")
except ValueError as e:
    check("sweep.bad_alg", "Unsupported" in str(e), str(e))

print(f"\n{passed} passed, {failed} failed.")
sys.exit(1 if failed else 0)
