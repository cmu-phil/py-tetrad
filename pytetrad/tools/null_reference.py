"""Parametric-bootstrap null reference for the Markov check.

This module is a thin Python front end for edu.cmu.tetrad.search.MarkovCheckNullReference
(requires a tetrad-current.jar containing that class). Given a dataset, a DAG D, and a
Markov-check test configuration, the Java side fits a simulator to (data, D), simulates B
datasets that satisfy D's factorization by construction, runs the identical Markov check on
each, and reports where the real data's check statistic falls in that null distribution.

Simulators:
  "gnm"    -- edu.cmu.tetrad.sem.TrainedDagSimulatorGNM (NN mechanisms, bootstrapped
              noise; realistic conditionals). The preferred null.
  "linear" -- linear-Gaussian SEM (SemPm/SemEstimator/simulateData). A clean
              in-class null; useful as a test-calibration baseline.

Read-out per test:
  empirical_p = fraction of null draws with ad_ind <= the real ad_ind.
  Real fails while the GNM null passes  => genuine graph/model inadequacy.
  GNM null also fails (small null ad_inds throughout) => test miscalibration or
  simulator leakage; compare with the linear null to separate those.
  Null ad_inds clustered near 1 => broken simulator (lost sampling variation).

The reference inherits the Markov check's one-sidedness: it certifies the implied
independencies, not the dependencies that missing edges fail to imply. It sharpens
"fails Markov" into a diagnosis; it does not turn "passes Markov" into an endorsement.
This module reports statistics only; decisions about the model belong to the user.

Typical use:

    import pytetrad.tools.TetradSearch as ts
    import pytetrad.tools.sweep as sw
    import pytetrad.tools.null_reference as nr

    def mc_test(s):  # the same test used for the sweep's Markov check
        s.use_basis_function_lrt(truncation_limit=3, alpha=0.01, use_for_mc=True)

    report = sw.sweep(search, "boss", "penaltyDiscount", [1, 2, 4], ...)
    i = report.select_by_markov_adequacy()   # a defaulted decision; yours to override
    ref = nr.for_sweep(df, report, i, mc_test, B=50)
    print(ref.report)
"""

import numpy as np

import pytetrad.tools.TetradSearch as ts
import pytetrad.tools.translate as tr
import jpype.imports  # noqa: F401  (JVM started by the imports above)

_SIMULATORS = ("gnm", "linear")


class NullReferenceReport:
    """Holds the real-data check statistics and the null distributions (mirrors the
    fields of the Java Result; the Java object itself is kept as .java)."""

    def __init__(self, java_result, simulator):
        self.java = java_result
        self.dag = java_result.getDag()
        self.B = int(java_result.getNumDraws())
        self.simulator = simulator
        self.real_ad_ind = float(java_result.getRealAdInd())
        self.real_frac_dep = float(java_result.getRealFractionDependent())
        self.null_ad_ind = [float(v) for v in java_result.getNullAdInd()]
        self.null_frac_dep = [float(v) for v in java_result.getNullFractionDependent()]
        self.timings = {"fit": java_result.getFitMillis() / 1000.0,
                        "simulate": java_result.getSimulateMillis() / 1000.0,
                        "check": java_result.getCheckMillis() / 1000.0}

    @property
    def empirical_p(self):
        """Fraction of null draws with ad_ind <= the real ad_ind (small => real is
        atypically bad for the null; resolution is 1/B)."""
        return float(self.java.getEmpiricalP())

    @property
    def empirical_p_frac(self):
        """Same idea on the rejection fraction (large fractions are bad, so the
        tail is >=)."""
        return float(self.java.getEmpiricalPFraction())

    @property
    def report(self):
        a = np.array(self.null_ad_ind)
        t = self.timings
        return (
            f"Markov-check null reference ({self.simulator}, B={self.B})\n"
            f"  real:  ad_ind = {self.real_ad_ind:.6f}   frac facts rejected = {self.real_frac_dep:.3f}\n"
            f"  null:  ad_ind median {np.median(a):.4f}  [q10 {np.quantile(a, .1):.4f},"
            f" q90 {np.quantile(a, .9):.4f}]  min {a.min():.4f}\n"
            f"  empirical p (ad_ind)        = {self.empirical_p:.3f}\n"
            f"  empirical p (frac rejected) = {self.empirical_p_frac:.3f}\n"
            f"  time (s): fit {t['fit']:.1f}, simulate {t['simulate']:.1f}, check {t['check']:.1f}"
        )

    def __str__(self):
        return self.report


def null_reference(df, graph, configure, B=50, simulator="gnm", n_sim=None,
                   base_seed=1000, gnm_params=None,
                   condition_set_type=None):
    """Compute a parametric-bootstrap null reference for the Markov check.

    df        : pandas DataFrame (the real data; dtypes per py-tetrad conventions).
    graph     : java Graph. A CPDAG is converted to a member DAG on the Java side;
                the DAG actually checked is available as report.dag.
    configure : callable(TetradSearch) that sets the Markov-check test with
                use_for_mc=True -- the same configuration used on the real data.
    B         : number of null draws (empirical-p resolution is 1/B).
    simulator : "gnm" or "linear".
    n_sim     : rows per simulated dataset (default: len(df)).
    base_seed : draw b uses seed base_seed + b (gnm); applied once to RandomUtil (linear).
    gnm_params: a TrainedDagSimulatorGNM.Params, or None for defaults.
    condition_set_type : an edu.cmu.tetrad.search.ConditioningSetType
                (default ORDERED_LOCAL_MARKOV_PROPERTY, matching TetradSearch.markov_check).
    """
    from edu.cmu.tetrad.search import MarkovCheckNullReference, ConditioningSetType

    if simulator not in _SIMULATORS:
        raise ValueError(f"unknown simulator: {simulator} (expected one of {_SIMULATORS})")

    # Harvest the Markov-check test wrapper + parameters from a configured TetradSearch,
    # so the null draws are checked with exactly the test used on the real data.
    s = ts.TetradSearch(df)
    configure(s)
    if s.MC_TEST is None:
        raise Exception("A test for the Markov Checker has not been set. In 'configure', call a "
                        "use_{test name} method with use_for_mc=True.")

    sim_type = (MarkovCheckNullReference.SimulatorType.TRAINED_DAG_GNM if simulator == "gnm"
                else MarkovCheckNullReference.SimulatorType.LINEAR_SEM)
    cst = condition_set_type or ConditioningSetType.ORDERED_LOCAL_MARKOV_PROPERTY

    data_j = tr.pandas_data_to_tetrad(df)
    result = MarkovCheckNullReference.compute(
        data_j, graph, s.MC_TEST, s.params, cst, sim_type,
        int(B), int(n_sim) if n_sim else -1, int(base_seed), gnm_params)

    return NullReferenceReport(result, simulator)


def for_sweep(df, sweep_report, index, configure, **kwargs):
    """Null reference for the point-estimate graph at a sweep setting.

    df           : the real data the sweep was run on.
    sweep_report : the SweepReport returned by pytetrad.tools.sweep.sweep.
    index        : the setting index (e.g., from select_by_markov_adequacy(),
                   which remains a defaulted decision -- yours to override).
    configure    : the same Markov-check test configuration used in the sweep.
    """
    graph = sweep_report.point_graph(index, java=True)
    return null_reference(df, graph, configure, **kwargs)
