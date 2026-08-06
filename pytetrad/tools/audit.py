"""Python conveniences for Tetrad's pre-search data audit (edu.cmu.tetrad.data.audit): a
battery of checks on a data matrix that bear on the choice and reliability of causal search
procedures - variable typing and cardinalities, small discrete cells, near-constant columns,
high correlation and near-determinism, marginal non-Gaussianity, sample adequacy, and
missingness. The audit reports findings, never recommendations; see TETRAD_ANALYSIS_GUIDE.md
for how to act on the finding codes. Requires a tetrad-current.jar built from development on
or after 2026-08-06.

Note py-tetrad's dtype convention (see translate.py): float columns become continuous Tetrad
variables; integer, category, and object columns become discrete. Integer-coded continuous
measurements should be cast to float before auditing (or pass int_as_cont=True), and the
audit itself will flag suspicious typing via CONTINUOUS_FEW_VALUES and DISCRETE_MANY_LEVELS.
"""

import jpype.imports

try:
    jpype.startJVM(classpath=["resources/tetrad-current.jar"])
except OSError:
    pass

import pandas as pd

import edu.cmu.tetrad.data.audit as ta
import pytetrad.tools.translate as tr


def _require():
    if not hasattr(ta, "DataAudit"):
        raise RuntimeError("This tetrad-current.jar lacks edu.cmu.tetrad.data.audit; "
                           "update to a jar built from development on or after 2026-08-06.")


# Threshold keyword arguments accepted by audit(), in the positional order of the Java
# Config constructor, with defaults mirroring the Java defaults (keep in sync with
# DataAudit.Config).
_CONFIG_DEFAULTS = [
    ("few_continuous_values", 5),
    ("many_discrete_levels", 10),
    ("small_cell_count", 10),
    ("min_expected_pairwise_cell", 5.0),
    ("high_correlation", 0.9),
    ("r2_determinism", 0.98),
    ("eta_squared_determinism", 0.95),
    ("ad_alpha", 0.01),
    ("min_ad_sample_size", 20),
    ("low_sample_ratio", 5.0),
    ("near_constant_frequency", 0.99),
    ("near_constant_variance", 1e-12),
]


class AuditResult:
    """Wraps a Java DataAudit. The full Java object is available as .java; the common
    consumables are the findings DataFrame, the text report, and the JSON rendering."""

    def __init__(self, java):
        self.java = java

    @property
    def findings(self):
        """The findings as a pandas DataFrame with columns code, severity, variables (a
        list of names), values (a dict of named statistics, thresholds included), and
        message. Empty DataFrame (with these columns) if nothing was flagged."""
        rows = [{"code": str(f.getCode()),
                 "severity": str(f.getSeverity()),
                 "variables": [str(v) for v in f.getVariables()],
                 "values": {str(k): float(v) for k, v in f.getValues().items()},
                 "message": str(f.getMessage())}
                for f in self.java.getFindings()]
        return pd.DataFrame(rows, columns=["code", "severity", "variables", "values", "message"])

    @property
    def report(self):
        """The human-readable multi-section report."""
        return str(self.java.report())

    @property
    def json(self):
        """The JSON rendering of the findings and summary statistics."""
        return str(self.java.toJson())

    def has(self, code):
        """True if any finding has the given code (a FindingCode name, e.g.
        'HIGH_CORRELATION')."""
        return any(str(f.getCode()) == code for f in self.java.getFindings())

    def __str__(self):
        return self.report


def audit(df, int_as_cont=False, **thresholds):
    """Audits a pandas DataFrame and returns an AuditResult.

    int_as_cont is forwarded to translate.pandas_data_to_tetrad: if True, integer columns
    are treated as continuous rather than discrete.

    Thresholds may be overridden by keyword; the accepted names and defaults are:
    few_continuous_values=5, many_discrete_levels=10, small_cell_count=10,
    min_expected_pairwise_cell=5.0, high_correlation=0.9, r2_determinism=0.98,
    eta_squared_determinism=0.95, ad_alpha=0.01, min_ad_sample_size=20,
    low_sample_ratio=5.0, near_constant_frequency=0.99, near_constant_variance=1e-12.
    Every finding also records the threshold it used, so results can be re-judged at other
    thresholds without re-running."""
    _require()

    unknown = set(thresholds) - {name for name, _ in _CONFIG_DEFAULTS}
    if unknown:
        raise TypeError(f"Unknown threshold(s): {sorted(unknown)}; "
                        f"accepted: {[name for name, _ in _CONFIG_DEFAULTS]}")

    data = tr.pandas_data_to_tetrad(df, int_as_cont=int_as_cont)

    if thresholds:
        args = [thresholds.get(name, default) for name, default in _CONFIG_DEFAULTS]
        config = ta.DataAudit.Config(*args)
        return AuditResult(ta.DataAudit(data, config))

    return AuditResult(ta.DataAudit(data))
