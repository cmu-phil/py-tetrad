## This script assumes that the user has pip-installed the pytetrad package. Here is now:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim

D, G = sim.simulateContinuous(num_meas=100, samp_size=1000)

D2 = tr.tetrad_data_to_pandas(D)
G2 = tr.graph_to_matrix(G)

# Save data to a file
D2.to_csv('../mydata.csv', index=False)
G2.to_csv('../mygraph.csv', index=False)
