import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

import jpype
import jpype.imports

jpype.startJVM("-Xmx40g", classpath=[f"{BASE_DIR}/tetrad-gui-7.2.2-launch.jar"])

from pytetrad.util import startJVM
startJVM()

from edu.cmu.tetrad.util import Params, Parameters
import edu.cmu.tetrad.algcomparison.simulation as sim
import edu.cmu.tetrad.algcomparison.graph as graph
import pytetrad.translate as tr

# An easy way to simulate data in Tetrad is to use the algorithm comparison tool.
# Here's an example.

params = Parameters()

params.set(Params.SAMPLE_SIZE, 500)
params.set(Params.NUM_MEASURES, 200)
params.set(Params.AVG_DEGREE, 6)
params.set(Params.NUM_LATENTS, 8)
params.set(Params.RANDOMIZE_COLUMNS, True)
params.set(Params.COEF_LOW, 0)
params.set(Params.COEF_HIGH, 1)
params.set(Params.VAR_LOW, 1)
params.set(Params.VAR_HIGH, 3)
params.set(Params.VERBOSE, False)
params.set(Params.NUM_RUNS, 1)

sim_ = sim.LinearFisherModel(graph.RandomForward())
sim_.createData(params, True)
data_model = sim_.getDataModel(0)
graph = sim_.getTrueGraph(0)

df = tr.tetrad_to_pandas(data_model)
gr = tr.tetrad_graph_to_causal_learn(graph)

print(df)
print(graph)

df.to_csv('../mydata.csv', index=False)

with open('../mygraph.txt', 'w') as f:
    f.write(str(gr))
# gr.to_csv('../mygraph.csv', index=False)



