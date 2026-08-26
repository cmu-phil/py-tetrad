"""
G-regression: total causal effects from an MPDAG.

This wraps Tetrad's ``edu.cmu.tetrad.search.GRegression``, a Java implementation of the estimator of
Guo and Perković (2022), "Efficient least squares for estimating total effects under linearity and causal
sufficiency" (JMLR 23(104)), also available in R as the package ``eff2``. Given

* an MPDAG (a CPDAG, possibly with background-knowledge orientations added and Meek-closed), and
* a continuous data set (or covariance matrix) over the graph's variables, assumed to come from a linear
  structural equation model with independent errors and no latent confounding,

it decides whether the total effect of a treatment set A on an outcome Y is identified and, if so, returns
the efficient least-squares estimate of it, with optional bootstrap standard errors.

Typical use with a graph learned by :class:`pytetrad.tools.TetradSearch.TetradSearch`::

    search = ts.TetradSearch(df)
    search.use_sem_bic()
    search.run_boss()
    gr = GRegression(search.get_java(), df)
    gr.is_identified(["X3"], "X7")
    gr.total_effect(["X3"], "X7")                # -> pandas Series indexed by treatment
    gr.bootstrap(["X3", "X5"], "X7", 200)         # -> {'effect': Series, 'se': Series, 'cov': DataFrame}

If some edges of the CPDAG are known to be oriented a particular way, use :func:`orient_with_knowledge`
to produce the corresponding MPDAG before constructing the estimator; more orientations mean more
effects become identified.

Cross-checked against ``eff2`` on the DAG, CPDAG, and MPDAG cases in
``tetrad-lib/src/test/resources/gregression_eff2_check.R``: identical identification verdicts and
estimates agreeing to ~1e-13. One caveat when comparing yourself: ``eff2`` requires an *unnamed*
adjacency matrix (no dimnames), or its bucket decomposition silently fails.
"""

import jpype
import jpype.imports

import importlib.resources as importlib_resources

jar_path = importlib_resources.files('pytetrad').joinpath('resources', 'tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

import numpy as np
import pandas as pd

import pytetrad.tools.translate as tr
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.utils as tsu
import edu.cmu.tetrad.util as tu
import java.util as util


def _as_list(x):
    if isinstance(x, str):
        return [x]
    return list(x)


def _names(nodes):
    return [str(n.getName()) for n in nodes]


def mpdag_problem(graph):
    """
    Returns None if ``graph`` is an MPDAG acceptable to G-regression, otherwise a string explaining why not
    (e.g., a bidirected edge, a directed cycle, or an edge Meek's rules would orient). Use this to check a
    graph before building a :class:`GRegression`.
    """
    problem = ts.GRegression.mpdagProblem(graph)
    return None if problem is None else str(problem)


def orient_with_knowledge(cpdag, knowledge=None, required=(), forbidden=()):
    """
    Returns a copy of ``cpdag`` with the given background knowledge imposed and then closed under Meek's
    orientation rules, i.e., the MPDAG representing the CPDAG plus that knowledge.

    Orientations may be given as a Tetrad ``Knowledge`` object and/or as lists of (tail, head) name pairs:
    ``required`` edges are oriented tail -> head, ``forbidden`` pairs forbid tail -> head (so an undirected
    edge between them is oriented the other way). The input graph is not modified.

    Raises ValueError if the result is not a valid MPDAG, which happens when the knowledge conflicts with the
    CPDAG (e.g., it requires an orientation that creates a cycle or contradicts a compelled edge).
    """
    know = td.Knowledge(knowledge) if knowledge is not None else td.Knowledge()
    for tail, head in required:
        know.setRequired(tail, head)
    for tail, head in forbidden:
        know.setForbidden(tail, head)

    mpdag = tg.EdgeListGraph(cpdag)
    meek = tsu.MeekRules()
    meek.setKnowledge(know)
    meek.setRevertToUnshieldedColliders(False)
    meek.setVerbose(False)
    meek.orientImplied(mpdag)

    problem = mpdag_problem(mpdag)
    if problem is not None:
        raise ValueError("Knowledge does not yield a valid MPDAG: " + problem)
    return mpdag


class GRegression:
    """
    Efficient least-squares estimator of total effects in a linear SEM whose causal structure is known up to
    an MPDAG. See the module docstring.

    :param graph: A Tetrad ``Graph`` that is an MPDAG: only directed and undirected edges, acyclic in its
        directed part, and closed under Meek's rules. CPDAGs from PC, FGES, BOSS, GRaSP, etc. qualify, as do
        DAGs. To add background knowledge to a CPDAG first, see :func:`orient_with_knowledge`.
    :param data: A pandas DataFrame of continuous data, or a Tetrad ``DataSet``, whose columns include every
        variable in the graph (matched by name). Required for :meth:`bootstrap`; otherwise ``cov`` may be
        given instead.
    :param cov: A Tetrad ``ICovarianceMatrix``, used instead of ``data`` if ``data`` is None.
    """

    def __init__(self, graph, data=None, cov=None):
        if data is None and cov is None:
            raise ValueError("Either data or cov must be given.")

        self.graph = graph
        self.data = None

        if data is not None:
            if isinstance(data, pd.DataFrame):
                data = data.astype({c: "float64" for c in data.columns})
                self.data = tr.pandas_data_to_tetrad(data)
            else:
                self.data = data
            cov = td.CovarianceMatrix(self.data)

        self.java = ts.GRegression(graph, cov)

    # ------------------------------------------------------------------ helpers

    def _node(self, name):
        node = self.graph.getNode(name)
        if node is None:
            raise ValueError(f"No variable named '{name}' in the graph.")
        return node

    def _node_list(self, names):
        lst = util.ArrayList()
        for name in _as_list(names):
            lst.add(self._node(name))
        return lst

    # ------------------------------------------------------------------ queries

    def is_identified(self, treatments, outcome):
        """
        True if the total effect of ``treatments`` (a name or list of names) on ``outcome`` is identified in
        the MPDAG, i.e., no proper possibly causal path from a treatment to the outcome starts with an
        undirected edge (Guo and Perković, Theorem 2 / Perković 2020).
        """
        return bool(self.java.isIdentified(self._node_list(treatments), self._node(outcome)))

    def total_effect(self, treatments, outcome):
        """
        The estimated total effect of ``treatments`` on ``outcome``: the vector of partial derivatives of
        E[Y | do(X_A = x_A)] with respect to each treatment.

        Returns a pandas Series indexed by treatment name, or a float if ``treatments`` is a single string.
        Raises ValueError if the effect is not identified.
        """
        names = _as_list(treatments)
        try:
            eff = self.java.totalEffect(self._node_list(names), self._node(outcome))
        except jpype.JException as e:
            raise ValueError(str(e.getMessage())) from None
        eff = np.array(list(eff), dtype=float)
        if isinstance(treatments, str):
            return float(eff[0])
        return pd.Series(eff, index=names, name=outcome)

    def bootstrap(self, treatments, outcome, num_bootstraps=100, seed=None):
        """
        The estimate together with a nonparametric bootstrap of its sampling distribution (rows of the data
        are resampled with replacement and the estimator re-fitted ``num_bootstraps`` times). Requires the
        estimator to have been built from ``data``, not ``cov``.

        Returns a dict with ``'effect'`` (Series), ``'se'`` (Series of bootstrap standard errors), and
        ``'cov'`` (DataFrame, the bootstrap covariance of the estimate). Pass ``seed`` for reproducibility.
        """
        if self.data is None:
            raise ValueError("bootstrap requires the estimator to be constructed from data, not a covariance.")
        if seed is not None:
            tu.RandomUtil.getInstance().setSeed(int(seed))

        names = _as_list(treatments)
        try:
            result = ts.GRegression.bootstrap(self.graph, self.data, self._node_list(names), self._node(outcome),
                                              int(num_bootstraps))
        except jpype.JException as e:
            raise ValueError(str(e.getMessage())) from None

        effect = np.array(list(result.effect()), dtype=float)
        se = np.array(list(result.standardErrors()), dtype=float)
        cov = tr.tetrad_matrix_to_numpy(result.covariance())
        return {
            "effect": pd.Series(effect, index=names, name=outcome),
            "se": pd.Series(se, index=names, name=outcome),
            "cov": pd.DataFrame(cov, index=names, columns=names),
        }

    def buckets(self):
        """
        The bucket decomposition of the MPDAG: the connected components of its undirected part, in a causal
        order, as a list of lists of variable names. Buckets are the units of the block-recursive
        regressions the estimator is built from.
        """
        return [_names(b) for b in self.java.getBuckets()]

    def lambda_(self):
        """
        The estimated reduced-form coefficient matrix Lambda (a DataFrame, rows = regressors, columns =
        responses): for each bucket B, the OLS coefficients of X_B on its external parents Pa(B), with zeros
        everywhere else. The total effect of A on Y is read off column Y of (I - Lambda_DD)^{-1} for
        D = An(Y) in the graph with edges into A removed.
        """
        nodes = self.java.getGraph().getNodes()
        names = _names(nodes)
        return pd.DataFrame(tr.tetrad_matrix_to_numpy(self.java.getLambda()), index=names, columns=names)

    def __str__(self):
        return f"GRegression over {len(self.buckets())} buckets: {self.buckets()}"


# ---------------------------------------------------------------------- static conveniences

def is_identified(graph, treatments, outcome):
    """Identification check on an MPDAG alone, with variables given by name; no data needed."""
    treat = util.HashSet()
    for name in _as_list(treatments):
        treat.add(graph.getNode(name))
    return bool(ts.GRegression.isIdentified(graph, treat, graph.getNode(outcome)))


def buckets(graph):
    """The bucket decomposition of an MPDAG, as a list of lists of names; no data needed."""
    return [_names(b) for b in ts.GRegression.bucketDecomposition(graph)]
