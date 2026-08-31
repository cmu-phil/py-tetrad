---
name: tetrad-analysis
description: Disciplined workflow for analyzing real datasets with Tetrad / py-tetrad causal discovery - audit the data, propose decisions for user approval, search with multiple algorithm families, sweep parameters with diagnostics, and report honestly. Use this skill whenever the user wants to run causal discovery, causal search, or structure learning on a real dataset with Tetrad, py-tetrad, TetradSearch, BOSS, FGES, GRaSP, PC, FCI, or LiNGAM; whenever they ask which algorithm, test, score, alpha, or penalty discount to use on their data; whenever they upload a dataset and mention causes, causal graphs, DAGs, CPDAGs, or PAGs; and whenever they ask to interpret a Tetrad output graph. Trigger even if they just say "find the causal structure in this data" without naming Tetrad.
---

# Tetrad Real-Data Analysis

A workflow for applying Tetrad's causal discovery algorithms to real data
without producing confidently wrong answers. The full guide, with a complete
worked example (Auto MPG) and the finding-code reference, is at
`TETRAD_ANALYSIS_GUIDE.md` in the py-tetrad repository root — read it when
you need the details behind any step below.

## The principle (non-negotiable)

*Agents assist; algorithms discover; scientists judge* (Zheng, Verma, Gill,
Dai, Spirtes & Zhang 2026, arXiv:2606.23608). You may audit data, explain
assumptions, propose methods and settings, run tools, and interpret outputs.
You may NOT supply edges, orientations, priors, or causal conclusions from
your own knowledge, and nothing you believe about the domain may enter the
discovery core except as an assumption the user has explicitly adopted.

**Rules of engagement.** Background knowledge (tiers, forbidden/required
edges), variable exclusions or mergers, type reassignments, transforms,
missing-data policies, and parameter choices all change what the algorithm
treats as input, so they are user decisions: propose them with reasons,
apply them only after the user approves, and record every adopted decision
in the final report. Never silently drop or recode a variable, convert a
temporal hint into a knowledge tier, or tune a threshold until the output
looks better. Present CPDAGs and PAGs as equivalence-class objects
conditioned on stated assumptions, never as confirmed causal facts.

## The workflow: Audit → Decide → Search → Diagnose → Report

Never run one algorithm with default settings and report the graph.

### 0. Provenance (ask the user; no software can answer these)

What does each variable mean and in what units? How was the sample
collected (selection effects)? Is there a defensible partial time order?
What plausible common causes are NOT measured — name them? Did the
data-generating regime change during collection? Write the answers down;
they become the Decisions section of the report.

### 1. Audit

```python
import pytetrad.tools.audit as au
result = au.audit(df)          # int_as_cont=True to treat int columns as continuous
print(result.report)
result.findings                # DataFrame: code, severity, variables, values, message
```

Mind py-tetrad's dtype convention: float columns → continuous; int,
category, and object columns → discrete. Integer-coded measurements must be
cast to float (the audit flags suspects via `CONTINUOUS_FEW_VALUES` and
`DISCRETE_MANY_LEVELS`). Interpret each finding code using Appendix A of the
guide — findings are facts about the data; the considerations they raise are
proposals for the user. For missing data, use `pytetrad/tools/missing.py`
(`audit`, `impute`, `imputation_search`) and propose a policy.

### 2. Decisions (propose; user approves)

Variable treatment (nominal vs. ordered-as-continuous), transforms (log for
skew IF using linear-Gaussian machinery; raw scale for LiNGAM or
basis-function runs), the *minimal defensible* knowledge tiers, the
latent-confounding stance (if the audit or provenance suggests latents,
plan a PAG search alongside any CPDAG search), and the missing-data policy.
Genuinely ambiguous calls become sensitivity runs, not agonized guesses.

### 3. Search — at least two algorithm families with different assumptions

Match machinery to the audit (guide Step 3 has the full table): mixed data →
conditional/degenerate Gaussian scores with BOSS/GRaSP/FGES; strong
non-Gaussianity → add a LiNGAM-family run to orient; nonlinearity →
basis-function scores or KCI/CCI; plausible latents → an FCI-family PAG
search. Agreement between methods with different failure modes is the most
persuasive robustness evidence available.

Findings nominate; Markov adequacy arbitrates. The audit table proposes
candidate families, never vetoes one: a family it disfavors may still reach
Markov adequacy (on Auto MPG, DG+BOSS/FGES passes despite flagged
nonlinearity), and a pass is relative to the checking test — confirm a pass
under a linear/CG test with a test that has power against the flagged
violation (KCI, CCI, basis-function LRT) before reporting adequacy.
Experimental engines on the development branch (e.g., the Cord family) are
opt-in only: propose them clearly labeled as experimental, and only when the
user asks for frontier methods or every released family fails Markov
adequacy after sweeping and repair; the user's adoption is a recorded
decision.

### 4. Sweep and diagnose

```python
import pytetrad.tools.TetradSearch as ts
import pytetrad.tools.sweep as sw

search = ts.TetradSearch(df)
# ... user-approved knowledge via search.add_to_tier(...)
search.use_conditional_gaussian_score()                 # score for the searches
search.use_conditional_gaussian_test(alpha=0.01, use_for_mc=True)  # Markov-check test

report = sw.sweep(search, "boss", "penaltyDiscount", [1.0, 2.0, 4.0],
                  num_resamples=100, seed=42)
print(report.table)    # per setting: num_edges, instability, ad_ind, frac_dep_dep
i = report.select_by_markov_adequacy()   # defaulted decision rule - surface it, let the user override
print(report.probability_graph(i))       # point estimate with bootstrap-style edge probabilities
```

Sweep penalty discount (score-based) or alpha (test-based). A good setting
has near-uniform Markov-check independence p-values (`ad_ind` not small),
high detection of implied dependencies (`frac_dep_dep`), and stable edges.

If the selected candidate is close but not adequate AND the graph is very
small (Auto MPG scale, roughly ≤ 15 nodes — candidate enumeration is
combinatorial), try Vertex Repair before declaring misspecification:

```python
import edu.cmu.tetrad.search as tsearch
import edu.cmu.tetrad.search.test as ttest
test = ttest.IndTestDegenerateGaussianLrt(tr.pandas_data_to_tetrad(df))
test.setAlpha(0.01)
repaired = tsearch.VertexRepairSearch(graph, test,
    tsearch.ConditioningSetType.ORDERED_LOCAL_MARKOV_PROPERTY).search()
# re-run markov_check on `repaired` with the same setup
```

Repair rules (guide Step 4.5): repair only marginal candidates — it can
REDUCE the adequacy of an already adequate graph, so re-check and keep the
better of the two; repair cannot rescue a misspecified setting (if it does
not reach adequacy, revisit Steps 2–3); and repair edits are decisions — the
report shows the pre-repair graph, the post-repair graph, the edit list, and
both Markov checks.

If NO setting is Markov-adequate even after repair, that is a finding — the
model family is misspecified; revisit Steps 2–3 rather than shipping the
least-bad graph.

Markov checks test only the graph's implied *independencies* (the
dependency side is summarized separately as `frac_dep_dep`), so denser
graphs imply fewer checkable facts and pass more easily — a complete graph
implies none at all. Two rules follow: report the number of implied facts
alongside every pass/fail verdict, and among models that pass the Markov
check, prefer the one with fewer edges. Never read a pass as strong
evidence for a dense graph without noting how little it asserted.
The selection helpers are defaulted decisions: show the table, state which
rule you applied, and let the user choose. Seeds pin the resample draws but
not internal tie-breaking in algorithms like FGES, so small run-to-run
wobble is normal.

### 5. Report

The deliverable is not one graph. Include: the provenance answers and every
adopted decision (as decisions); the audit findings that drove them; all
algorithms and settings run; the selected graph WITH bootstrap edge
probabilities; its Markov-check statistics; and a cross-algorithm edge
classification (agreed by all / by some / contested), with contested regions
called out honestly — typically the collinear clusters. Present IDA-style
effect estimates as bounds under the model, never as point causal effects.

## Common failure modes to catch yourself on

Integer columns silently treated as discrete; running FGES + SEM-BIC
defaults on mixed or non-Gaussian data; treating an ordered many-level
variable as nominal; reporting a bare graph without bootstrap frequencies or
a Markov check; reading every directed CPDAG edge as an established causal
claim; ignoring near-determinism and then blaming the algorithm for
"unstable results"; choosing alpha or penalty by whichever value gives the
most interesting graph; repairing an already-adequate graph, or reporting a
repaired graph without the edit trail and both Markov checks; declaring
misspecification without sweeping, or declaring adequacy from a check whose
test has no power against the violation the audit flagged.
