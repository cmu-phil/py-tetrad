## This script assumes that the user has pip-installed the pytetrad package. Here is now:
## pip install git+https://github.com/cmu-phil/py-tetrad

## Exercises the Observational Study simulation (archetype: Algerian Forest Fires).
## Roles: context variables (exogenous drivers, some discrete), system variables,
## near-deterministic index chains, and outcomes.

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim

# 1. i.i.d. version at defaults, with a discrete (fire/no-fire style) outcome.
D, G, sim_ = sim.simulateObservationalStudy(discrete_outcome=True, samp_size=1000)

df = tr.tetrad_data_to_pandas(D)
print("Variables:", list(df.columns))
print(df.head(8))
print()
print("True graph:")
print(G)

# 2. Serial version: the true graph is a time lag graph with maximum lag 1 by our
# time-series conventions; the contemporaneous summary graph comes from the sim object.
D2, G2, sim2 = sim.simulateObservationalStudy(max_lag=1, samp_size=1000)
print()
print("Serial version -- true lag graph:")
print(G2)
print()
print("Contemporaneous summary graph:")
print(sim2.getContemporaneousGraph(0))

# 3. Panel version: subjects are independent replicates with random intercepts, which
# act as latent confounding once rows are pooled. Subject boundaries matter for lagging
# and for block bootstrap.
D3, G3, sim3 = sim.simulateObservationalStudy(num_subjects=5, max_lag=1, samp_size=1000)
starts = sim3.getSubjectStarts(0)
print()
print("Panel version -- subject start rows:", list(starts))
