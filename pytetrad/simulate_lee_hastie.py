## This script assumes that the user has pip-installed the pytetrad package. Here is now:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim

## Simulates data with both continuous and discrete columns.
D, G = sim.simulateLeeHastie(num_meas=100, samp_size=1000)

D = tr.tetrad_data_to_pandas(D)
G = tr.graph_to_matrix(G)

# Save data to a file
D.to_csv('../mydata.csv', index=False)
G.to_csv('../mygraph.csv', index=False)
