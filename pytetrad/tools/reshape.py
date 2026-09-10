"""Python convenience for Tetrad's long-to-wide reshaping (edu.cmu.tetrad.data.LongToWide): one row per unit
per occasion (e.g., one row per student per assessment) becomes one row per unit, with one column per occasion per
measured variable. This is the reshaping a causal search needs when the rows of a file are not the units of
analysis; searching the long table would treat each unit's repeated rows as independent cases.

    import pytetrad.tools.reshape as rs
    wide, report, keys = rs.long_to_wide(df, row_keys='anon_student_id', column_key='assessment',
                                         value_vars=['pct_first_try_correct'])
    print(report)          # units, levels, fill rate per column, duplicates resolved
    result = au.audit(wide)  # then the usual audit

A (unit, level) combination absent from the long data becomes a missing value in the wide data. A combination
present more than once (a second attempt, say) is resolved by the aggregation policy, which defaults to 'fail'
so duplicates are never silently collapsed; the alternatives are 'first', 'last', 'mean', 'min', 'max', 'sum',
and 'count' ('count' gives the number of long rows as a continuous column, zero where a unit has none).

Requires a tetrad-current.jar built from development on or after 2026-09-10. Mind py-tetrad's dtype convention:
the column key and row keys should be object (string) or category columns so that they become discrete Tetrad
variables; pass int_as_cont=True to treat integer-coded measurements as continuous.
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

import java.util as util
import edu.cmu.tetrad.data as td
import pytetrad.tools.translate as tr


def _require():
    if not hasattr(td, "LongToWide"):
        raise RuntimeError("This tetrad-current.jar lacks edu.cmu.tetrad.data.LongToWide; "
                           "update to a jar built from development on or after 2026-09-10.")


def _aggregation(name):
    try:
        return td.LongToWide.Aggregation.valueOf(str(name).upper())
    except Exception:
        raise ValueError(f"Unknown aggregation '{name}'; expected one of fail, first, last, mean, min, max, sum, count.")


def long_to_wide(df, row_keys, column_key, value_vars=None, aggregation='fail', aggregations=None,
                 sanitize_names=True, keep_row_keys=False, separator='.', int_as_cont=False):
    """Reshapes a long-format pandas DataFrame to wide format through Tetrad's LongToWide.

    Args:
        df: The long data.
        row_keys: A column name, or list of names, whose joint values identify a unit (one wide row each).
        column_key: The column whose levels become column suffixes; must become a discrete Tetrad variable.
        value_vars: The columns to spread (each yields one wide column per level, named value<separator>level).
            None (the default) means every column that is not a key.
        aggregation: The default policy for duplicated (unit, level) combinations; see the module docstring.
        aggregations: Optional dict from value column name to a policy overriding the default for that column.
        sanitize_names: If True, runs of characters other than letters, digits, '_', '.', '-' in wide column names
            are replaced by '_', so the names survive knowledge files and other whitespace-delimited contexts.
        keep_row_keys: If True, the row key column(s) are kept as leading (discrete) columns of the wide data.
        separator: Between the value column name and the level suffix.
        int_as_cont: Passed to pandas_data_to_tetrad for the long data.

    Returns:
        (wide, report, unit_keys): the wide DataFrame (row order = order of first appearance of each unit), the
        findings-only report string, and a list of the row-key values of each wide row.
    """
    _require()
    if isinstance(row_keys, str):
        row_keys = [row_keys]

    data = tr.pandas_data_to_tetrad(df, int_as_cont=int_as_cont)
    t = td.LongToWide(column_key, jpype.JArray(jpype.JString)(list(row_keys)))

    if value_vars is not None:
        jl = util.ArrayList()
        for v in value_vars:
            jl.add(v)
        t.setValueVariables(jl)

    t.setDefaultAggregation(_aggregation(aggregation))
    for v, a in (aggregations or {}).items():
        t.setAggregation(v, _aggregation(a))

    t.setSanitizeNames(bool(sanitize_names))
    t.setKeepRowKeys(bool(keep_row_keys))
    t.setSeparator(separator)

    result = t.apply(data)
    wide = tr.tetrad_data_to_pandas(result.wide())
    keys = [[str(s) for s in k] for k in result.unitKeys()]
    return wide, str(result.report()), keys
