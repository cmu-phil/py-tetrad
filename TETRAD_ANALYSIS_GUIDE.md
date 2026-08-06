# Analyzing Real Data with Tetrad: A Field Guide

This guide describes a discipline for applying Tetrad's causal discovery
algorithms to real datasets. It is written both for human users and for AI
assistants (see `WRITING_TETRAD_CODE_WITH_CLAUDE.md`): if you are asking
Claude or another model to help you analyze a dataset with py-tetrad, point
it at this document and it will follow the workflow below.

The core discipline is:

> **Audit → Decide → Search → Diagnose → Report.**

Never run a single algorithm with default settings on a real dataset and
report the resulting graph. Every step below exists because skipping it is a
documented way to get confidently wrong answers.

**Division of labor.** This guide follows the principle argued by Zheng,
Verma, Gill, Dai, Spirtes & Zhang (2026): *agents assist; algorithms
discover; scientists judge*. AI assistants can audit data, explain
assumptions, propose methods and settings, run tools, and interpret partially
identified outputs — but causal evidence comes only from data, explicit
assumptions, and formal algorithms with their diagnostics. Nothing a language
model believes about the domain may enter the discovery core except as an
assumption the user has explicitly adopted. Accordingly, the measurement
machinery referenced here (`DataAudit`, the Markov check, bootstrap
resampling, parameter sweeps) lives in Tetrad's Java core and emits findings
and statistics, never recommendations; the judgment lives in this document
and in the conversation between the user and their assistant.

**Rules of engagement for AI assistants following this guide.** Background
knowledge (tiers, forbidden/required edges), variable exclusions or mergers,
type reassignments, transforms, missing-data policies, and parameter choices
all change what the algorithm treats as input, so they are *user decisions*.
Propose them, with reasons; apply them only after the user approves; and
record every adopted decision in the final report. Never silently drop or
recode a variable, convert a temporal hint into a knowledge tier, or adjust a
threshold until the output looks better. When interpreting results, present
CPDAGs and PAGs as the equivalence-class objects they are, conditioned on the
stated assumptions — not as confirmed causal facts.

All code samples were checked against `pytetrad/tools/TetradSearch.py`,
`audit.py`, and `sweep.py` on the main branch and `tetrad-current.jar` built
from the Tetrad `development` branch (August 2026; the audit and sweep APIs
require a jar built on or after 2026-08-06). If a method is missing in your
installation, update the jar and py-tetrad checkout.

---

## Step 0: Understand provenance (questions no software can answer)

Before loading anything, answer in writing:

1. **What does each variable mean, in what units, measured how?**
2. **How was the sample collected?** Is it a random sample of some population,
   a convenience sample, or (commonly) *everything that exists* — products on
   a market, patients at one clinic, countries? Selection into the sample is a
   causal process too, and it can induce dependencies (selection bias).
3. **Is there a defensible partial time order?** Variables that are fixed
   before others are determined (year, country of origin, demographic
   attributes) give you background-knowledge tiers for free.
4. **What plausible common causes are *not* measured?** List them by name.
   If several measured variables are all plausibly driven by one unmeasured
   factor ("engine size", "socioeconomic status", "disease severity"), expect
   trouble in that cluster and plan a latent-variable (PAG) search alongside
   any DAG-space search.
5. **Did the data-generating regime change during collection?** (New
   regulations, instrument recalibration, policy shifts.) If so, either model
   time explicitly or expect the "one fixed DAG" assumption to be strained.

Write the answers down. They become the Decisions section of your report, and
they are the part of the analysis a rule engine cannot do for you.

## Step 1: Audit the data matrix

Load the data and compute, at minimum:

| Check | Why it matters | Typical response |
|---|---|---|
| Variable types and cardinalities | Every test/score assumes a type model; nominal vs. ordinal vs. count vs. continuous is *your* call, not the file's | Declare types explicitly; see dtype note below |
| Cell counts for discrete variables (marginal and pairwise) | Discrete and conditional-Gaussian tests condition on cells; tiny cells (n < ~10) destroy them | Merge categories, treat as continuous, or drop |
| Near-constant columns | No information, numerical instability | Drop |
| Pairwise correlations and near-determinism | \|r\| ≳ 0.9 or a variable nearly a function of others → unstable CI decisions, unfaithfulness, plausible latent | Note the cluster; expect instability there; consider a PAG search |
| Marginal non-Gaussianity (e.g. Anderson–Darling) | Linear-Gaussian tests/scores are misspecified — but non-Gaussianity is an *asset* for LiNGAM-family methods | Transform, use basis-function/nonparametric machinery, or exploit with LiNGAM |
| Nonlinearity (scatterplot matrix of key pairs) | Linear tests can miss or distort nonlinear dependence | Transform to linearity, or use basis-function scores / KCI / CCI |
| Missingness pattern | Listwise deletion is only safe under MCAR | Use `MissingDataAudit` / `pytetrad/tools/missing.py`: audit, then testwise, EM, or multiple imputation via `set_missing_data_policy` |
| n vs. p, and n vs. conditioning-set sizes | Small n bounds the depth of conditioning you can trust | Restrict depth; prefer score-based; be modest |

In py-tetrad, the whole battery runs in one call (`edu.cmu.tetrad.data.audit`
on the Java side; requires a jar built from `development` on or after
2026-08-06):

```python
import pandas as pd
import pytetrad.tools.audit as au

df = pd.read_csv("data.txt", sep="\t")

result = au.audit(df)          # or au.audit(df, int_as_cont=True)
print(result.report)           # human-readable findings
result.findings                # DataFrame: code, severity, variables, values, message
```

Every finding carries the statistic *and* the threshold that fired it, so
results can be re-judged without re-running; thresholds are overridable by
keyword (e.g. `au.audit(df, high_correlation=0.95)`). The audit reports
findings, never recommendations — Appendix A maps each finding code to the
considerations it should raise. Missingness details beyond the summary
finding are in `pytetrad/tools/missing.py` (`audit`, `impute`,
`imputation_search`).

**py-tetrad dtype convention (important).** `translate.py` maps **float
columns to continuous variables and everything else — including plain
integer columns — to discrete variables.** Real datasets very often load
numeric columns as `int64`. If you do nothing, py-tetrad will treat a column
like `weight` with 346 distinct integer values as a 346-category discrete
variable. Always cast explicitly:

```python
continuous = ["mpg", "displacement", "horsepower", "weight", "acceleration"]
df = df.astype({c: "float64" for c in continuous})
# columns intended as discrete stay int (or use .astype("category"))
```

## Step 2: Decisions to make before searching

Record each of these explicitly; they are analysis choices, not defaults.

1. **Variable treatment.** For each column: continuous, ordinal-as-continuous,
   or nominal? An ordered variable with many levels (a year, a stage) is
   usually better as continuous than as a k-category nominal — crossing many
   categories with other discretes shreds cell counts. A nominal variable
   (region, type) must stay discrete. When a call is genuinely ambiguous
   (a 5-level count variable, say), plan to run it both ways as a
   sensitivity check rather than agonizing.
2. **Transforms.** If you will use linear-Gaussian machinery (Fisher-Z,
   SEM-BIC, conditional Gaussian), log-transform strongly right-skewed
   positive variables and check that key scatterplots look linear afterward.
   If you will use basis-function scores, KCI/CCI, or LiNGAM-family methods,
   prefer the raw scale — for LiNGAM, non-Gaussianity is the signal.
3. **Background knowledge.** Write the *minimal defensible* tier ordering:
   only orderings you would defend to a hostile referee (temporal
   precedence, logical impossibility). If a stronger ordering is available
   but contestable, run both and report whether conclusions change.
   In py-tetrad: `search.add_to_tier(tier, var_name)`. Knowledge is a
   constraint on the discovery algorithm itself, so tiers suggested by an
   assistant (or by a repository's knowledge file) are proposals until the
   user adopts them.
4. **Latent-confounding stance.** If Step 0 produced named candidate latents,
   commit in advance to running a PAG-space search (FCIT, BOSS-FCI, GFCI, …)
   alongside any CPDAG-space search, and to reporting where they disagree.
5. **Missing-data policy.** From the audit: MCAR-plausible and low rate →
   testwise deletion; MAR-plausible → EM covariance (continuous) or multiple
   imputation (`set_missing_data_policy("multiple_imputation", ...)`).

## Step 3: Choosing algorithms — considerations, not a decision tree

There is no lookup table from data to algorithm; there are considerations:

| Data regime | Test/score family | Search families |
|---|---|---|
| Continuous, ~linear, ~Gaussian after transforms | SEM-BIC / EBIC; Fisher-Z | BOSS, GRaSP, FGES (score); PC-family (test) |
| Continuous, clearly non-Gaussian, ~linear | Same as above for adjacencies, **plus** ICA-LiNGAM / DirectLiNGAM / FASK to orient from distributional asymmetry | `run_direct_lingam()`, `run_lingam()`, `run_fask()` |
| Continuous, nonlinear | Basis-function BIC / LRT; KCI; CCI | BOSS/GRaSP with basis-function score; PC-family with KCI/CCI |
| Mixed continuous + discrete | Conditional Gaussian, Degenerate Gaussian, basis-function (mixed) | BOSS/GRaSP/FGES with CG/DG score |
| All discrete | BDeu, discrete BIC; chi-square/G-square | Same searches |
| Latent confounding plausible | Same tests/scores | FCIT, BOSS-FCI, GRaSP-FCI, GFCI (PAG output) |
| Small n relative to p | Prefer scores over deep CI testing; restrict depth | Score-based searches; report humbly |

Two rules of thumb:

- **Always run at least two algorithm families whose assumptions differ**
  (e.g., a score-based CPDAG search and a LiNGAM-family or PAG search).
  Agreement between methods with different failure modes is the single most
  persuasive robustness evidence available on real data.
- **Never report an algorithm's output at a parameter setting you did not
  examine alternatives to.** That is Step 4.

## Step 4: Parameter sweeps and diagnostics

For score-based searches sweep `penalty_discount` (e.g. {1, 2, 4}); for
test-based searches sweep `alpha` (e.g. {0.001, 0.01, 0.05}). At each
setting, compute three things:

1. **The point-estimate graph.**
2. **A Markov check**: does the estimated graph's implied conditional
   independence structure fit the data? `markov_check` returns, among other
   statistics, an Anderson–Darling p-value for the uniformity of the
   p-values of implied independencies (`ad_ind`) — near-zero means the model
   asserts independencies the data reject; the fraction of implied
   *dependencies* judged dependent (`frac_dep_dep`) should be high.
3. **Bootstrap edge stability**: rerun under resampling and record edge
   frequencies (`set_bootstrapping`).

In py-tetrad, the whole loop is one call to the sweep harness
(`edu.cmu.tetrad.algcomparison.sweep` on the Java side), which draws the
resamples once and shares them across settings so comparisons are paired.
Using the mixed-data setup from the worked example below:

```python
import pytetrad.tools.TetradSearch as ts
import pytetrad.tools.sweep as sw

search = ts.TetradSearch(df)
for i, tier in enumerate(tiers):                       # user-approved knowledge
    for v in tier:
        search.add_to_tier(i, v)
search.use_conditional_gaussian_score()                # score for the searches
search.use_conditional_gaussian_test(alpha=0.01, use_for_mc=True)  # MC test

report = sw.sweep(search, "boss", "penaltyDiscount", [1.0, 2.0, 4.0],
                  num_resamples=100, seed=42)
print(report.table)      # per setting: num_edges, instability, ad_ind, frac_dep_dep
print(report.markdown)   # the same as a pasteable table

i = report.select_by_markov_adequacy()   # a defaulted decision rule, yours to override
print(report.point_graph(i))             # the point estimate at that setting
print(report.probability_graph(i))       # with bootstrap-style edge probabilities
```

The selection helpers (`select_by_markov_adequacy`, `select_by_instability`,
`select_most_stable`) are explicit, overridable decision rules, not evidence
— the report exists precisely so the choice can be inspected and defended.
Note on reproducibility: `seed` makes the resampled row sets exactly
reproducible, but algorithms with internal thread pools (e.g. FGES) can
break score near-ties differently between runs, so small run-to-run wobble
in instabilities is possible and expected.

Choose the setting where (a) the Markov-check independence p-values are
closest to uniform (`ad_ind` not small), (b) implied dependencies are
overwhelmingly detected (`frac_dep_dep` high), and (c) bootstrap edge
frequencies are stable in the neighborhood of the setting. If no setting
satisfies (a), that is a finding: the model family is misspecified for this
data — revisit Step 2/3 rather than shipping the least-bad graph.

Finally, overlay the surviving graphs from your different algorithm families
and classify each edge: agreed by all, agreed by some, contested.

## Step 5: Reporting

A defensible real-data report contains:

1. The provenance answers and every Step 2 decision, stated as decisions.
2. The audit findings that drove them.
3. All algorithms and settings run, not just the winner.
4. The selected graph **with bootstrap edge frequencies attached** — never a
   bare graph.
5. Markov-check statistics for the selected graph.
6. The cross-algorithm agreement classification, with contested regions
   called out honestly (typically the collinear clusters).
7. If effect sizes are wanted: IDA-style bounds (`Ida`/`IdaCheck`) computed
   on the selected CPDAG, presented as *bounds under the model*, not point
   causal effects.

---

## Worked example: the Auto MPG dataset

Data: `example-causal-datasets/real/auto-mpg` (392 cars × 8 variables,
tab-delimited, header row; UCI Auto MPG with the 6 rows missing `horsepower`
already removed). Variables: `mpg`, `cylinders`, `displacement`,
`horsepower`, `weight`, `acceleration`, `modelyear` (70–82), `origin`
(1 = US, 2 = Europe, 3 = Japan).

### Step 0 — provenance

Cars sold on the US market, 1970–1982. The sample is "everything that
existed," so mild market-selection effects are possible. `modelyear` and
`origin` are unambiguously exogenous. An obvious unmeasured factor:
regulatory pressure (CAFE standards, 1975 on) drives the mpg trend across
years and is not in the data — `modelyear` partly proxies for it. A second
one: "vehicle/engine class" plausibly drives `cylinders`, `displacement`,
`weight`, and `horsepower` jointly, which predicts trouble (and motivates a
PAG search) in exactly that cluster.

### Step 1 — audit (actual numbers)

Running `au.audit(df)` on the raw load fires `DISCRETE_MANY_LEVELS`,
`NEAR_DETERMINISM_DISCRETE_CONTINUOUS`, `SMALL_MARGINAL_CELL`, and
`SMALL_PAIRWISE_CELLS` — the integer columns were silently discrete, and the
audit catches it. After the Step 2 typing below, the audit reports:

- No missing values in this version (but say so: the original had 6 missing
  `horsepower` rows, listwise-deleted upstream — benign at 6/398).
- **Types:** all columns load as `int64` or `float64`; five load as ints.
  Under py-tetrad's dtype convention that would make `weight` a
  346-category discrete variable. Cast before doing anything else.
- **Cardinalities / cells:** `cylinders` ∈ {3,4,5,6,8} with counts
  {4, 199, 3, 83, 103} — the 3- and 5-cylinder cells are unusable as
  categories. `modelyear` has 13 ordered levels. `origin` has 3.
- **Collinearity:** displacement–weight r = 0.93, displacement–horsepower
  0.90, horsepower–weight 0.86. Within cylinder classes, displacement SD is
  21–47 against between-class means of 110–345: `cylinders` is nearly a
  deterministic coarsening of `displacement`.
- **Non-Gaussianity:** Anderson–Darling rejects normality decisively for
  everything except `acceleration` (AD statistics 3.5–17.4 vs. a 1% critical
  value ≈ 1.03; `horsepower` skew 1.08). The mpg–weight and mpg–horsepower
  relationships are visibly curved (roughly reciprocal).
- **n/p:** 392/8 — comfortable for shallow conditioning, adequate overall.

### Step 2 — decisions

1. **Types:** `origin` nominal discrete (unordered nationality).
   `modelyear` continuous (an ordered trend; 13 categories crossed with
   other discretes would shred cells). `cylinders`: ambiguous — nearly
   deterministic in `displacement`, with two tiny cells. Primary analysis
   treats it as continuous; sensitivity run merges {3,4,5} and treats it as
   3-category discrete.
2. **Transforms:** for the linear-Gaussian runs, log `displacement`,
   `horsepower`, `weight` (this substantially linearizes the mpg
   relationships). LiNGAM runs use the raw scale.
3. **Knowledge (minimal defensible):** tier 0 = {`modelyear`, `origin`};
   tier 1 = {`cylinders`, `displacement`, `horsepower`, `weight`};
   tier 2 = {`acceleration`, `mpg`}. The repo's knowledge file also places
   `weight` in tier 0 — that is a contestable modeling commitment (weight is
   plausibly a consequence of design choices), so we run both and report
   whether conclusions change.
4. **Latents:** the engine-class cluster motivates a PAG search.
5. **Missingness:** none; nothing to do.

```python
import numpy as np
import pandas as pd
import pytetrad.tools.TetradSearch as ts

df = pd.read_csv("auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
cont = ["mpg", "displacement", "horsepower", "weight",
        "acceleration", "modelyear", "cylinders"]
df = df.astype({c: "float64" for c in cont})          # origin stays int64
for c in ["displacement", "horsepower", "weight"]:     # linear-Gaussian runs
    df[c] = np.log(df[c])

tiers = [["modelyear", "origin"],
         ["cylinders", "displacement", "horsepower", "weight"],
         ["acceleration", "mpg"]]
```

### Steps 3–4 — searches, sweep, diagnostics

**Primary: BOSS with the conditional-Gaussian score** (discrete set =
{`origin`} only), penalty discount swept over {1, 2, 4}, knowledge tiers
set, 100 bootstrap resamples, Markov check with the CG test — exactly the
sweep call shown in Step 4 above. Expectations to check against, given the
audit: penalty 1 should overconnect the engine cluster; the modelyear→mpg
and weight→mpg edges should be stable at every setting; edges *within*
{displacement, horsepower, weight, cylinders} should show unstable
orientation and lower bootstrap frequencies at every setting.

**Secondary (distributional orientation):** DirectLiNGAM on the raw-scale
continuous subset — `search.run_direct_lingam()` — as an independent check
on orientations the CPDAG leaves unresolved. The strong non-Gaussianity is
what licenses this.

**Tertiary (latent check):** FCIT (`search.run_fcit()`) or BOSS-FCI with the
same score/test and knowledge. Prediction registered in advance: part of the
engine cluster returns bidirected or circle marks, reflecting the latent
vehicle-class factor.

**Sensitivity runs:** (a) cylinders-as-discrete with merged small cells;
(b) the repo's stronger knowledge with `weight` in tier 0; (c) basis-function
BIC (`use_basis_function_bic`) on the raw scale as a nonlinearity-robust
replication of the primary run.

### Step 5 — what the report looks like

The deliverable is *not* one graph. It is: the decision log above; the sweep
table (per penalty: Markov-check `ad_ind`, `frac_dep_dep`, edge count,
bootstrap stability); the selected CPDAG with bootstrap frequencies printed
on edges; the PAG next to it; and an edge-classification summary of the
form "found by all of {CG-BOSS, DirectLiNGAM, FCIT}" / "contested." On this
dataset, expect the honest summary to be: the downstream structure
(weight/horsepower → mpg, acceleration; modelyear → mpg) is stable and
agreed; the internal wiring of the engine cluster is not identifiable from
this data and is likely confounded by an unmeasured class factor. That
second sentence is a *finding*, and reporting it is the point of the
discipline.

---

## Appendix A: finding codes and the considerations they raise

The audit emits findings, not recommendations; this table is the judgment
layer, and it is deliberately documentation rather than code so it can
evolve. Each code below names what is true of the data and what an analyst
(human or AI assistant, proposing for user approval) should weigh in
response.

| Code | What it means | Considerations |
|---|---|---|
| `CONTINUOUS_FEW_VALUES` | A continuous variable takes few distinct values | Was it meant to be discrete? Or a count/ordinal best left continuous? Check the dtype conversion (int columns become discrete in py-tetrad; floats continuous) |
| `DISCRETE_MANY_LEVELS` | A discrete variable has many observed levels | If ordered (year, stage, dose), continuous treatment usually beats k categories; if nominal, expect small cells when crossed with other discretes |
| `NEAR_CONSTANT` | A column is (nearly) constant | Usually drop; it carries no information and can destabilize numerics |
| `SMALL_MARGINAL_CELL` | A discrete category has very few cases | Merge categories, treat as continuous if ordered, or accept unreliable tests involving it |
| `SMALL_PAIRWISE_CELLS` | A discrete pair has small expected cells | Conditional independence tests conditioning on this pair are unreliable; restrict depth or restructure the variables |
| `HIGH_CORRELATION` | A continuous pair is very highly correlated | Expect unstable edges within the cluster; consider whether a latent common cause explains it (→ PAG search); check bootstrap probabilities there before believing orientations |
| `EXACT_LINEAR_DEPENDENCE` | The continuous correlation matrix is singular | A variable is redundant; remove one of the involved variables before searching |
| `NEAR_DETERMINISM_CONTINUOUS` | A variable is nearly a linear function of the others | Near-faithfulness violation; expect unstable CI decisions; consider removing or combining variables |
| `NEAR_DETERMINISM_DISCRETE_CONTINUOUS` | A discrete variable nearly determines a continuous one | The discrete is close to a coarsening of the continuous (auto-mpg's cylinders/displacement); including both adds instability without information |
| `NON_GAUSSIAN` (INFO) | A marginal deviates from Gaussian | Threat to linear-Gaussian machinery (transform, or use basis-function/nonparametric tests) but an asset for LiNGAM-family orientation — often worth an extra run, not just a fix |
| `LOW_SAMPLE_RATIO` | Few rows per variable | Prefer score-based searches, restrict conditioning depth, report humbly with wide bootstrap intervals |
| `MISSING_DATA` (INFO) | Missing values present | Read the delegated missingness audit; choose a policy (testwise, EM, multiple imputation) as a visible decision — see `pytetrad/tools/missing.py` |

## Appendix B: pitfalls seen in practice

- **Integer columns silently treated as discrete** in py-tetrad (see Step 1).
- Running FGES + SEM-BIC defaults on mixed or non-Gaussian data because it
  is the first example found.
- Treating an ordered many-level variable (year, dose, stage) as nominal.
- Reporting a bare graph with no bootstrap frequencies or Markov check.
- Interpreting every directed edge in a CPDAG as an established causal
  claim, and interpreting IDA outputs as point effects rather than bounds.
- Ignoring near-determinism, then debugging "unstable results" that are in
  fact faithfulness violations.
- Choosing alpha or penalty by whichever value gives the most interesting
  graph.

---

## References

Zheng, Y., Verma, V., Gill, M., Dai, H., Spirtes, P., & Zhang, K. (2026).
Causal discovery in the era of agents. arXiv:2606.23608. (The
assistance-versus-evidence principle this guide's division of labor
follows, instantiated for the causal-learn ecosystem in causal-learn+.)

