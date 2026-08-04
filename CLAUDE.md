# CLAUDE.md — py-tetrad project guidance

This project accesses the Tetrad causal discovery library (Java) from Python
via py-tetrad and JPype. Follow the rules below when writing or modifying code.

## Environment

- Python 3.14, JPype1 (`pip install JPype1`), pandas, numpy.
- JDK 21 (Tetrad requires 21+). `JAVA_HOME` must point to it.
- Tetrad is provided by the jar `pytetrad/resources/tetrad-current.jar`
  (or a project-local copy of it). This jar is the latest published beta
  built from the `development` branch of https://github.com/cmu-phil/tetrad.
  The jar changes over time.

## Source of truth for the Tetrad API

- The Tetrad API you are calling is defined by the `development` branch of
  https://github.com/cmu-phil/tetrad (current working branches may exist,
  e.g. `joe-work-2026-8-4`, but code here should target `development`).
- Do NOT rely on memorized Tetrad class names, packages, or signatures —
  they change between versions. Before using any Tetrad class or method,
  verify it against the development-branch source (fetch the file from
  GitHub or read a local clone) or the published Javadocs.
- Key packages: `edu.cmu.tetrad.data`, `edu.cmu.tetrad.graph`,
  `edu.cmu.tetrad.search`, `edu.cmu.tetrad.search.score`,
  `edu.cmu.tetrad.search.test`, `edu.cmu.tetrad.algcomparison`.
- Parameter meanings and defaults are documented in the Tetrad manual:
  https://tetrad-manual.readthedocs.io/en/latest/

## JPype rules (important)

1. Start the JVM ONCE, before importing any Java package, e.g.:

   ```python
   import jpype
   import jpype.imports

   if not jpype.isJVMStarted():
       jpype.startJVM(classpath=["pytetrad/resources/tetrad-current.jar"])

   import edu.cmu.tetrad.search as ts
   ```

2. Never call `jpype.startJVM` twice in one process; guard with
   `jpype.isJVMStarted()`. Design scripts so all JVM work happens in a
   single process.
3. Give the JVM memory if needed: `jpype.startJVM("-Xmx4g", classpath=[...])`.
4. Convert Java values coming back to Python explicitly (`str(...)`,
   `int(...)`, list comprehension over Java lists) before handing them to
   pandas/numpy.

## py-tetrad conventions

- For standard "run a search on a DataFrame" workflows, prefer the wrapper
  `pytetrad/tools/TetradSearch.py` — it hides JPype details and exposes
  methods to select scores/tests, set knowledge, and run searches.
- For anything the wrapper does not cover, call Tetrad classes directly
  via JPype.
- Translate data and graphs with `pytetrad/tools/translate.py`:
  pandas DataFrame -> Tetrad DataSet before searching, and Tetrad graphs
  back to Python structures afterward. Do not pass pandas objects into
  Tetrad methods directly.
- Column dtypes matter: integer columns are treated as discrete and
  float columns as continuous by the translators; cast columns
  deliberately before translating.
- Follow the runnable examples in `pytetrad/` (e.g. `run_continuous.py`)
  as the canonical patterns.
- Background knowledge uses `edu.cmu.tetrad.data.Knowledge` (tiers,
  required/forbidden edges); set it on the search or via TetradSearch.

## Workflow expectations

- After writing a script, run it and fix errors until it executes cleanly.
- If a Tetrad class or method cannot be found at runtime, assume the jar
  and your assumed API are out of sync: re-check the development branch
  source for the current name/signature, and note the discrepancy.
- Print result graphs in a readable form (e.g. `print(graph)`) and, where
  useful, also convert them for downstream Python use.
- Keep scripts small and self-contained; put shared helpers in a module.

## Things to avoid

- Do not invent Tetrad classes, methods, or parameters.
- Do not use deprecated entry points from old Tetrad versions without
  checking they still exist on the development branch.
- Do not start the JVM at import time of a library module in a way that
  prevents callers from configuring the classpath; provide an explicit
  init function or guard.
