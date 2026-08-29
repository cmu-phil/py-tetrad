## This script assumes that the user has pip-installed the pytetrad package. Here is now:
## pip install git+https://github.com/cmu-phil/py-tetrad

## Exercises the Designed Experiment simulation (archetype: NASA Airfoil Self-Noise).
## Tiers: grid-valued design factors F1..., near-deterministic derived intermediates D1...,
## interaction-heavy responses R1....

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim

# Airfoil-like settings: 4 factors, 1 derived, 1 response, rows sorted into
# configuration blocks with a CONFIG bookkeeping column appended.
D, G, sim_ = sim.simulateDesignedExperiment(num_factors=4, num_derived=1, num_responses=1,
                                            coupling=0.5, sort_by_configuration=True,
                                            emit_config_column=True, samp_size=1500)

df = tr.tetrad_data_to_pandas(D)
print("Variables:", list(df.columns))
print(df.head(12))
print()
print("True graph (pre-selection DAG):")
print(G)

starts = sim_.getConfigurationStarts(0)
print()
print("Number of configuration blocks:", len(starts))
print("First few block start rows:", list(starts[:10]))

# Remember to exclude the CONFIG column from search; it is bookkeeping, the analogue
# of TOWN in the corrected Boston Housing data.
