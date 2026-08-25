"""Python conveniences for Tetrad's pre-search data audit (edu.cmu.tetrad.data.audit): a
battery of checks on a data matrix that bear on the choice and reliability of causal search
procedures - variable typing and cardinalities, small discrete cells, near-constant columns,
high correlation and near-determinism, marginal non-Gaussianity, serial dependence of rows
in file order, sample adequacy, and missingness. The audit reports findings, never
recommendations; see TETRAD_ANALYSIS_GUIDE.md for how to act on the finding codes. Requires
a tetrad-current.jar built from development on or after 2026-08-06; the serial dependence
settings (the serial_* and min_serial_sample_size keywords below) additionally require a jar
built on or after 2026-08-10, and are gracefully skipped at their defaults against older
jars.

The SERIAL_DEPENDENCE check is one-sided with respect to row order: a flag means rows are
dependent in the order given (so independence tests assuming i.i.d. rows may be
anticonservative), but a clean result does not rule out dependence under some other row
ordering (e.g., if a time series was shuffled before saving). If the dataset concatenates
blocks (regions, subjects, sessions), pass the block column's name as serial_group_variable
so autocorrelations are computed within blocks; otherwise block-level mean shifts and
boundary jumps contaminate the pooled estimate.

Note py-tetrad's dtype convention (see translate.py): float columns become continuous Tetrad
variables; integer, category, and object columns become discrete. Integer-coded continuous
measurements should be cast to float before auditing (or pass int_as_cont=True), and the
audit itself will flag suspicious typing via CONTINUOUS_FEW_VALUES and DISCRETE_MANY_LEVELS.
"""

import jpype
import jpype.imports

# Start the JVM on the package's own jar (works both pip-installed and from the source tree);
# the same block as translate.py, so whichever tools module is imported first wins harmlessly.
import importlib.resources as importlib_resources
_jar_path = str(importlib_resources.files('pytetrad').joinpath('resources', 'tetrad-current.jar'))
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), "-ea",
                       "--enable-native-access=ALL-UNNAMED", classpath=[_jar_path])
    except OSError:
        print("can't load jvm")

import pandas as pd

import edu.cmu.tetrad.data.audit as ta
import pytetrad.tools.translate as tr


def _require():
    if not hasattr(ta, "DataAudit"):
        raise RuntimeError("This tetrad-current.jar lacks edu.cmu.tetrad.data.audit; "
                           "update to a jar built from development on or after 2026-08-06.")


# Threshold keyword arguments accepted by audit(), in the positional order of the Java
# Config constructor, with defaults mirroring the Java defaults (keep in sync with
# DataAudit.Config). _LEGACY_DEFAULTS is the 12-argument constructor of jars built before
# 2026-08-10; _SERIAL_DEFAULTS are the serial dependence settings appended by the full
# constructor of later jars.
_LEGACY_DEFAULTS = [
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

_SERIAL_DEFAULTS = [
    ("serial_max_lag", 5),
    ("serial_alpha", 0.01),
    ("serial_min_abs_autocorrelation", 0.2),
    ("min_serial_sample_size", 20),
    ("serial_group_variable", None),
]

_CONFIG_DEFAULTS = _LEGACY_DEFAULTS + _SERIAL_DEFAULTS


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

    @property
    def lag1_autocorrelations(self):
        """Lag-1 autocorrelation in file order per continuous variable name, as a dict, for
        those variables with enough observed values (within groups, if serial_group_variable
        was passed). Empty dict against jars that predate the serial dependence check."""
        if not hasattr(self.java, "getLag1Autocorrelations"):
            return {}
        return {str(k): float(v) for k, v in self.java.getLag1Autocorrelations().items()}

    @property
    def serial_p_values(self):
        """Ljung-Box p-value per continuous variable name, as a dict, testing the joint null
        that the first serial_max_lag autocorrelations in file order are zero. Empty dict
        against jars that predate the serial dependence check."""
        if not hasattr(self.java, "getSerialDependencePValues"):
            return {}
        return {str(k): float(v) for k, v in self.java.getSerialDependencePValues().items()}

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
    low_sample_ratio=5.0, near_constant_frequency=0.99, near_constant_variance=1e-12,
    serial_max_lag=5, serial_alpha=0.01, serial_min_abs_autocorrelation=0.2,
    min_serial_sample_size=20, serial_group_variable=None.
    Every finding also records the threshold it used, so results can be re-judged at other
    thresholds without re-running.

    serial_group_variable names a discrete column (in Tetrad's typing after translation, so
    an integer/category/object column of df unless int_as_cont interferes) within whose
    groups row autocorrelations are computed; use it whenever the file stacks blocks such as
    regions or subjects. Naming an absent or continuous column raises. serial_max_lag=0
    disables the serial dependence check."""
    _require()

    unknown = set(thresholds) - {name for name, _ in _CONFIG_DEFAULTS}
    if unknown:
        raise TypeError(f"Unknown threshold(s): {sorted(unknown)}; "
                        f"accepted: {[name for name, _ in _CONFIG_DEFAULTS]}")

    data = tr.pandas_data_to_tetrad(df, int_as_cont=int_as_cont)

    if thresholds:
        args = [thresholds.get(name, default) for name, default in _CONFIG_DEFAULTS]

        try:
            config = ta.DataAudit.Config(*args)
        except TypeError:
            # The jar predates the serial dependence settings. If none of them were
            # explicitly requested, fall back to the legacy 12-argument constructor;
            # otherwise the request cannot be honored.
            if any(name in thresholds for name, _ in _SERIAL_DEFAULTS):
                raise RuntimeError(
                    "This tetrad-current.jar predates the serial dependence settings; "
                    "update to a jar built from development on or after 2026-08-10 to use "
                    f"{sorted(name for name, _ in _SERIAL_DEFAULTS)}.") from None
            config = ta.DataAudit.Config(*args[:len(_LEGACY_DEFAULTS)])

        return AuditResult(ta.DataAudit(data, config))

    return AuditResult(ta.DataAudit(data))
