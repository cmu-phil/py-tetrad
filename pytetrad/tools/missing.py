"""Python conveniences for Tetrad's missing-data support (edu.cmu.tetrad.data.missing):
auditing missingness, multiple imputation, and pooled imputation search. Requires a
tetrad-current.jar built from development on or after 2026-08-05."""

import jpype.imports

try:
    jpype.startJVM(classpath=["resources/tetrad-current.jar"])
except OSError:
    pass

import edu.cmu.tetrad.data.missing as tm
import edu.cmu.tetrad.util as util
import pytetrad.tools.translate as tr


def _require():
    if not hasattr(tm, "MissingDataAudit"):
        raise RuntimeError("This tetrad-current.jar lacks edu.cmu.tetrad.data.missing; "
                           "update to a jar built from development on or after 2026-08-05.")


def audit(df):
    """Returns the MissingDataAudit report string for a pandas DataFrame (per-variable missing
    rates, complete rows, patterns, pairwise counts, and Little's MCAR test for continuous
    data). Use the Java class directly for programmatic access to the numbers."""
    _require()
    return str(tm.MissingDataAudit(tr.pandas_data_to_tetrad(df)).report())


def impute(df, m=10, seed=-1, imputer=None):
    """Returns m completed copies of df as pandas DataFrames. imputer=None auto-selects:
    MvnImputer for all-continuous data, MiceLiteImputer for discrete or mixed data."""
    _require()
    data = tr.pandas_data_to_tetrad(df)
    if imputer is None:
        imputer = tm.MvnImputer() if data.isContinuous() else tm.MiceLiteImputer()
    return [tr.tetrad_data_to_pandas(d) for d in imputer.impute(data, m, seed)]


def imputation_search(df, algorithm, parameters=None, m=10, seed=-1, imputer=None):
    """Runs ImputationSearch: impute m completed datasets, run the algcomparison algorithm on
    each, and pool by edge frequency. Returns (pooled_graph, [per_imputation_graphs]) as Java
    Graph objects."""
    _require()
    if parameters is None:
        parameters = util.Parameters()
    spec = tm.MissingDataSpec.multipleImputation(m).withSeed(seed)
    result = tm.ImputationSearch.search(tr.pandas_data_to_tetrad(df), algorithm, parameters,
                                        imputer, spec)
    return result.pooledGraph, list(result.imputationGraphs)
