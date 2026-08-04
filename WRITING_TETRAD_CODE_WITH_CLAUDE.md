# Writing py-tetrad Code with Claude

One of the pleasant surprises of the py-tetrad approach — accessing [Tetrad](https://github.com/cmu-phil/tetrad) directly from Python via [JPype](https://github.com/jpype-project/jpype) — is how well it pairs with AI coding assistants such as [Claude](https://claude.com) (including [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)). Because py-tetrad exposes the *entire* Tetrad Java API to Python, rather than a hand-curated wrapper for a fixed list of algorithms, an assistant that can read the Tetrad source and Javadocs can write working causal-search code for essentially anything in the Tetrad codebase — algorithms, tests, scores, graph utilities, simulation tools, and so on — without waiting for anyone to write a binding for it.

This document explains how to set that up, what to watch out for, and provides a `CLAUDE.md` file you can drop into your own project so that Claude (especially Claude Code) has the context it needs to write correct code on the first try.

## Why this works well

- **The full API is available.** JPype gives Python direct access to every public class and method in the Tetrad jar. There is no wrapper layer that can be out of date or incomplete. If a method exists in Tetrad, Claude can call it from Python.
- **The source of truth is public.** Tetrad's [development branch](https://github.com/cmu-phil/tetrad/tree/development) and its Javadocs are on GitHub and Maven Central. Claude can be pointed at these to check signatures, package paths, and parameter names instead of guessing.
- **The idioms are small and learnable.** Once Claude knows the handful of py-tetrad conventions — starting the JVM before any Tetrad import, translating pandas DataFrames with `pytetrad.tools.translate`, and using `TetradSearch.py` for the common cases — the rest is ordinary Java-API-driven programming, which Claude is good at.
- **Examples act as few-shot prompts.** The runnable examples in [`pytetrad/`](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad) (e.g., `run_continuous.py`) show the correct patterns end to end. Telling Claude to imitate them dramatically improves output quality.

## Quick start

1. Follow the [install instructions in the README](https://github.com/cmu-phil/py-tetrad#install): JDK 21+ with `JAVA_HOME` set, a recent Python (3.12+; these instructions assume 3.14), `pip install JPype1`, and py-tetrad itself.
2. Copy the `CLAUDE.md` below (or the copy of it in this repository) into the root of your own project.
3. If you use **Claude Code**, it will pick up `CLAUDE.md` automatically. If you use the **Claude app or claude.ai**, paste the contents of `CLAUDE.md` at the start of your conversation, or add it to a Project's knowledge.
4. Ask for what you want in plain language, for example:

   > "Load `mydata.csv` with pandas, treat all columns as continuous, run BOSS with an SEM BIC score (penalty discount 2), and print the resulting CPDAG. Use py-tetrad conventions."

   or, for something with no pre-made wrapper:

   > "Using JPype and the Tetrad development-branch API, simulate 1000 samples from a random 20-node linear SEM, run PC with the Fisher Z test at alpha 0.01, and compare the estimated graph to the true CPDAG using the adjacency precision/recall statistics in `edu.cmu.tetrad.algcomparison.statistic`."

## Tips for getting good results

- **Tell Claude which jar you are using.** This repository maintains a current launch jar in [`pytetrad/resources`](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/resources) (referred to below as `tetrad-current.jar`), which tracks the latest published beta from Tetrad's development branch. The jar changes over time; ask Claude to verify any API it uses against the [development branch source](https://github.com/cmu-phil/tetrad/tree/development) rather than relying on memory.
- **Ask it to check, not recall.** Class names, package paths, and constructor signatures in Tetrad evolve. A prompt like "check the signature of `edu.cmu.tetrad.search.Boss` on the development branch before writing the call" is cheap insurance. Claude Code can clone or fetch the Tetrad repo and read the source directly.
- **Point it at the examples.** "Follow the pattern in `pytetrad/run_continuous.py`" is one sentence and saves a great deal of correction.
- **Prefer `TetradSearch.py` for standard workflows.** For the common search-on-a-DataFrame case, [`pytetrad/tools/TetradSearch.py`](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/tools/TetradSearch.py) hides all the JPype machinery. Ask Claude to use it unless you need something it doesn't cover.
- **Have Claude run the code.** With Claude Code, ask it to execute the script and iterate until it runs. JPype errors (wrong `JAVA_HOME`, JVM started twice, type-conversion issues) are much easier to fix interactively.
- **Consult the manual for parameters.** All algorithms, tests, scores, and parameters are documented in the [Tetrad ReadTheDocs manual](https://tetrad-manual.readthedocs.io/en/latest/); Claude can be pointed there for parameter semantics and defaults.

## Common pitfalls Claude should be warned about (the CLAUDE.md below does this)

- Importing Tetrad classes before `jpype.startJVM(classpath=[...])` has been called.
- Calling `startJVM` twice in one process (the JVM can be started only once).
- Passing pandas objects to Tetrad methods directly instead of translating them with `pytetrad.tools.translate` (`pandas_data_to_tetrad`, `tetrad_graph_to_pcalg`, etc.).
- Mixing up Java and Python types (e.g., Java `String` vs. Python `str`; use `str(...)` when bringing values back).
- Using stale class names remembered from older Tetrad versions rather than checking the development branch.

## The CLAUDE.md file

Copy everything in the block below into a file named `CLAUDE.md` at the root of your project (a ready-made copy is also included in this repository).

````markdown
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
````

## A note on scope

Everything above applies equally to plain-JPype scripts, `TetradSearch.py`-based workflows, Jupyter notebooks, and (via [rpy-tetrad](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/)) R workflows that route through this repository. And, as the README says of py-tetrad itself: once Claude has shown you the pattern a few times, you may find you no longer need much help at all — the ladder can be tossed away.

## Citation

If Claude helps you produce results you publish, please still cite py-tetrad:

> Ramsey, J., & Andrews, B. (2023, November). Py-Tetrad and RPy-Tetrad: A New Python Interface with R Support for Tetrad Causal Search. In *Causal Analysis Workshop Series* (pp. 40–51). PMLR.
