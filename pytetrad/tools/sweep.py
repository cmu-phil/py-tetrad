"""Python conveniences for Tetrad's parameter-sweep harness
(edu.cmu.tetrad.algcomparison.sweep): evaluate a search over a grid of parameter settings
and record, per setting, the point-estimate graph, bootstrap-style edge probabilities over
shared resamples, the StARS adjacency instability, and Markov-check statistics. Requires a
tetrad-current.jar built from development on or after 2026-08-06.

The sweep executes and measures; it does not decide. The selection helpers on SweepReport
(select_by_instability, select_most_stable, select_by_markov_adequacy) are explicit,
overridable decision rules, and choosing a setting remains the user's call - see
TETRAD_ANALYSIS_GUIDE.md and Zheng et al. (2026), arXiv:2606.23608.

Reproducibility: under a fixed seed the resampled row sets are exactly reproducible, but
end-to-end reproducibility of the report additionally requires the searched algorithm to be
deterministic; algorithms with internal thread pools (e.g. FGES) can break score near-ties
differently between runs, producing small run-to-run wobble in instabilities and in edges
near stability thresholds.

Typical use:

    import pytetrad.tools.TetradSearch as ts
    import pytetrad.tools.sweep as sw

    search = ts.TetradSearch(df)
    search.use_sem_bic()                      # score for the searches
    search.use_fisher_z(use_for_mc=True)      # test for the Markov check
    report = sw.sweep(search, "boss", "penaltyDiscount", [1.0, 2.0, 4.0],
                      num_resamples=100, seed=42)
    print(report.markdown)
    i = report.select_by_markov_adequacy()    # a defaulted decision; yours to override
    print(report.point_graph(i))
"""

import jpype.imports

try:
    jpype.startJVM(classpath=["resources/tetrad-current.jar"])
except OSError:
    pass

import pandas as pd

import edu.cmu.tetrad.algcomparison.sweep as tsweep
import edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag as cpdag
import edu.cmu.tetrad.search as ts
import java.util as jutil


def _require():
    if not hasattr(tsweep, "ParameterSweep"):
        raise RuntimeError("This tetrad-current.jar lacks edu.cmu.tetrad.algcomparison.sweep; "
                           "update to a jar built from development on or after 2026-08-06.")


def _build_algorithm(search, algorithm):
    """Builds the algcomparison wrapper for the named algorithm from the TetradSearch's
    configured score/test wrappers, mirroring the construction in TetradSearch.run_*."""
    name = algorithm.lower()

    score_based = {"fges": cpdag.Fges, "boss": cpdag.Boss, "sp": cpdag.Sp}
    if name in score_based:
        if search.SCORE is None:
            raise Exception(f"Algorithm '{algorithm}' needs a score; call a use_* score "
                            "method on the TetradSearch first (e.g. use_sem_bic()).")
        return score_based[name](search.SCORE)

    if name == "grasp":
        if search.SCORE is None or search.TEST is None:
            raise Exception("Algorithm 'grasp' needs both a score and a test; call use_* "
                            "score and test methods on the TetradSearch first.")
        return cpdag.Grasp(search.TEST, search.SCORE)

    if name == "pc":
        if search.TEST is None:
            raise Exception("Algorithm 'pc' needs a test; call a use_* test method on the "
                            "TetradSearch first (e.g. use_fisher_z()).")
        return cpdag.Pc(search.TEST)

    raise ValueError(f"Unsupported algorithm '{algorithm}'; supported: fges, boss, grasp, "
                     "sp, pc. (Other algcomparison wrappers can be swept by using the Java "
                     "ParameterSweep directly.)")


class SweepReport:
    """Wraps a Java SweepReport. The full Java object is available as .java; the common
    consumables are the table DataFrame, the markdown and JSON renderings, the selection
    helpers (which return row indices into the table), and per-index graph accessors."""

    def __init__(self, java):
        self.java = java
        self._results = list(java.getResults())

    @property
    def table(self):
        """One row per setting, aligned with the selection helpers' returned indices:
        the swept parameter columns, then num_edges, instability, ad_ind, frac_dep_dep,
        and elapsed_ms. Markov columns are NaN if no Markov check was run."""
        rows = []

        for r in self._results:
            row = {str(k): _unbox(v) for k, v in r.getSetting().items()}
            row["num_edges"] = int(r.getPointGraph().getNumEdges())
            row["instability"] = float(r.getAdjacencyInstability())
            mc = r.getMarkovStats()
            row["ad_ind"] = float(mc.adInd()) if mc is not None else float("nan")
            row["frac_dep_dep"] = float(mc.fracDepDep()) if mc is not None else float("nan")
            row["elapsed_ms"] = int(r.getElapsedMillis())
            rows.append(row)

        return pd.DataFrame(rows)

    @property
    def markdown(self):
        """The markdown rendering of the report."""
        return str(self.java.toMarkdown())

    @property
    def json(self):
        """The JSON rendering of the report."""
        return str(self.java.toJson())

    def point_graph(self, i, java=False):
        """The point-estimate graph for setting index i, as a string (default) or as the
        Java Graph object (java=True)."""
        g = self._results[i].getPointGraph()
        return g if java else str(g)

    def probability_graph(self, i, java=False):
        """The probability-annotated resample-aggregate graph for setting index i (edge
        probabilities display as for bootstrap results), as a string (default) or as the
        Java Graph object (java=True); None if no resamples were run."""
        g = self._results[i].getEdgeProbabilityGraph()
        if g is None:
            return None
        return g if java else str(g)

    def markov_stats(self, i):
        """The Markov-check statistics for setting index i as a dict, or None if no Markov
        check was run."""
        mc = self._results[i].getMarkovStats()
        if mc is None:
            return None
        return {"ad_ind": float(mc.adInd()), "ad_dep": float(mc.adDep()),
                "ks_ind": float(mc.ksInd()), "ks_dep": float(mc.ksDep()),
                "binomial_ind": float(mc.binomialInd()), "binomial_dep": float(mc.binomialDep()),
                "frac_dep_ind": float(mc.fracDepInd()), "frac_dep_dep": float(mc.fracDepDep()),
                "num_tests_ind": int(mc.numTestsInd()), "num_tests_dep": int(mc.numTestsDep())}

    def select_by_instability(self, cutoff):
        """StARS rule: the index of the setting with the largest instability strictly below
        the cutoff, or None if no setting qualifies. A defaulted decision rule, not
        evidence."""
        return self._index_of(self.java.selectByInstability(float(cutoff)))

    def select_most_stable(self):
        """The index of the setting with the smallest instability, or None. A defaulted
        decision rule, not evidence."""
        return self._index_of(self.java.selectMostStable())

    def select_by_markov_adequacy(self):
        """The index of the setting with the largest Anderson-Darling p for the implied
        independencies, ties broken by the larger fraction of implied dependencies
        detected; None if no setting has Markov statistics. A defaulted decision rule, not
        evidence."""
        return self._index_of(self.java.selectByMarkovAdequacy())

    def _index_of(self, result):
        if result is None:
            return None
        for i, r in enumerate(self._results):
            if r is result or r.equals(result):
                return i
        return None

    def __str__(self):
        return self.markdown


def _unbox(v):
    """Converts a Java boxed setting value to the corresponding Python scalar."""
    try:
        return float(v) if float(v) != int(v) else int(v)
    except (TypeError, ValueError):
        return str(v)


def sweep(search, algorithm, parameter, values, parameter2=None, values2=None,
          num_resamples=50, percent_resample_size=1.0, with_replacement=True, seed=-1,
          markov_check=True, conditioning_set_type=None, parallelized=True, verbose=False):
    """Sweeps one parameter (or the cross product of two) of the named algorithm and
    returns a SweepReport.

    search: a TetradSearch already configured with the score/test the algorithm needs
    (use_* methods), any knowledge (add_to_tier etc.), and - if markov_check is True - a
    Markov-check test (a use_* test method called with use_for_mc=True). Knowledge set on
    the TetradSearch is applied to the swept algorithm.

    algorithm: one of "fges", "boss", "grasp", "sp", "pc".

    parameter, values: the Params name to sweep and its values (e.g. "penaltyDiscount",
    [1.0, 2.0, 4.0]). parameter2/values2 optionally add a second, fastest-varying
    dimension.

    num_resamples resamples of percent_resample_size * n rows (with_replacement or not)
    are drawn once and shared across settings, so instability comparisons are paired;
    seed >= 0 makes the draws reproducible. markov_check runs the Markov check on each
    point graph with the TetradSearch's MC test; conditioning_set_type is a
    ts.ConditioningSetType or its name (default ORDERED_LOCAL_MARKOV_PROPERTY)."""
    _require()

    alg = _build_algorithm(search, algorithm)
    alg.setKnowledge(search.knowledge)

    harness = tsweep.ParameterSweep(alg, search.params)
    harness.setNumResamples(int(num_resamples))
    harness.setPercentResampleSize(float(percent_resample_size))
    harness.setWithReplacement(bool(with_replacement))
    harness.setSeed(int(seed))
    harness.setParallelized(bool(parallelized))
    harness.setVerbose(bool(verbose))

    if markov_check:
        if search.MC_TEST is None:
            raise Exception("markov_check=True but no Markov-check test is set on the "
                            "TetradSearch; call a use_* test method with use_for_mc=True "
                            "(e.g. use_fisher_z(alpha=0.01, use_for_mc=True)), or pass "
                            "markov_check=False.")
        harness.setMarkovCheckTest(search.MC_TEST)

        if conditioning_set_type is not None:
            if isinstance(conditioning_set_type, str):
                conditioning_set_type = ts.ConditioningSetType.valueOf(conditioning_set_type)
            harness.setConditioningSetType(conditioning_set_type)

    jvalues = jutil.ArrayList()
    for v in values:
        jvalues.add(v)

    if parameter2 is None:
        report = harness.sweep(search.data, parameter, jvalues)
    else:
        jvalues2 = jutil.ArrayList()
        for v in values2:
            jvalues2.add(v)
        report = harness.sweep(search.data, parameter, jvalues, parameter2, jvalues2)

    return SweepReport(report)
