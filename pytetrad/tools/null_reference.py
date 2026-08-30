"""Parametric-bootstrap null reference for the Markov check (prototype).

Given a dataset, a DAG D, and a Markov-check test configuration, this module
fits a simulator to (data, D), simulates B datasets that satisfy D's
factorization by construction, runs the identical Markov check on each, and
reports where the real data's check statistic falls in that null distribution.

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

This module reports statistics only; decisions about the model belong to the
user. Typical use:

    import pytetrad.tools.TetradSearch as ts
    import pytetrad.tools.sweep as sw
    import null_reference as nr

    def mc_test(s):  # the same test used for the sweep's Markov check
        s.use_basis_function_lrt(truncation_limit=3, alpha=0.01, use_for_mc=True)

    report = sw.sweep(search, "boss", "penaltyDiscount", [1, 2, 4], ...)
    i = report.select_by_markov_adequacy()
    ref = nr.for_sweep(df, report, i, mc_test, B=50)   # null ref for the selected graph
    print(ref.report)
"""

import time
import numpy as np
import pandas as pd

import pytetrad.tools.TetradSearch as ts
import pytetrad.tools.translate as tr
import jpype.imports  # noqa: F401  (JVM started by the imports above)


class NullReferenceReport:
    """Holds the real-data check statistics and the null distributions."""

    def __init__(self, dag, B, simulator, real, null_ad, null_frac, timings):
        self.dag = dag                    # the checked DAG (java Graph)
        self.B = B
        self.simulator = simulator
        self.real_ad_ind = real[0]        # AD p for uniformity of independence-fact p-values
        self.real_frac_dep = real[1]      # fraction of independence facts judged dependent
        self.null_ad_ind = list(null_ad)
        self.null_frac_dep = list(null_frac)
        self.timings = dict(timings)      # seconds: fit, simulate, check

    @property
    def empirical_p(self):
        """Fraction of null draws with ad_ind <= the real ad_ind (small => real is
        atypically bad for the null; resolution is 1/B)."""
        return float(np.mean([x <= self.real_ad_ind for x in self.null_ad_ind]))

    @property
    def empirical_p_frac(self):
        """Same idea on the rejection fraction (large fractions are bad, so the
        tail is >=)."""
        return float(np.mean([x >= self.real_frac_dep for x in self.null_frac_dep]))

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


def _check(df, dag, configure):
    """Run the Markov check with the configured test; return (ad_ind, frac_dep_ind)."""
    s = ts.TetradSearch(df)
    configure(s)
    res = s.markov_check(dag)
    return float(res[0]), float(res[6])


def null_reference(df, graph, configure, B=50, simulator="gnm", n_sim=None,
                   base_seed=1000, gnm_params=None, verbose=False):
    """Compute a parametric-bootstrap null reference for the Markov check.

    df        : pandas DataFrame (the real data; dtypes per py-tetrad conventions).
    graph     : java Graph. A CPDAG is converted to a member DAG via dagFromCpdag;
                the DAG actually checked is available as report.dag.
    configure : callable(TetradSearch) that sets the Markov-check test with
                use_for_mc=True -- the same configuration used on the real data.
    B         : number of null draws (empirical-p resolution is 1/B).
    simulator : "gnm" or "linear".
    n_sim     : rows per simulated dataset (default: len(df)).
    """
    from edu.cmu.tetrad.graph import GraphTransforms
    from edu.cmu.tetrad.sem import SemPm, SemEstimator, TrainedDagSimulatorGNM

    n_sim = n_sim or len(df)
    dag = graph if graph.paths().isLegalDag() else GraphTransforms.dagFromCpdag(graph)
    data_j = tr.pandas_data_to_tetrad(df)

    real = _check(df, dag, configure)

    t0 = time.time()
    if simulator == "gnm":
        params = gnm_params or TrainedDagSimulatorGNM.Params()
        model = TrainedDagSimulatorGNM(data_j, dag, params)
        model.fit()
        draw = lambda b: tr.tetrad_data_to_pandas(
            model.simulate(n_sim, base_seed + b).toDataSet()).astype(float)
    elif simulator == "linear":
        sem_im = SemEstimator(data_j, SemPm(dag)).estimate()
        draw = lambda b: tr.tetrad_data_to_pandas(
            sem_im.simulateData(n_sim, False)).astype(float)
    else:
        raise ValueError(f"unknown simulator: {simulator}")
    t_fit = time.time() - t0

    null_ad, null_frac, t_sim, t_chk = [], [], 0.0, 0.0
    for b in range(B):
        t0 = time.time()
        sim_df = draw(b)
        t_sim += time.time() - t0
        t0 = time.time()
        ad, frac = _check(sim_df, dag, configure)
        t_chk += time.time() - t0
        null_ad.append(ad)
        null_frac.append(frac)
        if verbose:
            print(f"  draw {b + 1}/{B}: ad_ind = {ad:.4f}, frac = {frac:.3f}")

    return NullReferenceReport(dag, B, simulator, real, null_ad, null_frac,
                               {"fit": t_fit, "simulate": t_sim, "check": t_chk})


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
