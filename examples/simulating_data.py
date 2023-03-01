import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

from pytetrad.util import startJVM
startJVM()

# Note: This is an example of how to write an algcomparison script to do algorithm
# comparison in Tetrad. It may not be the best example yet, but it does make
# clear how the script can be written. JR 2023-02-27

from edu.cmu.tetrad.util import Params, Parameters

import edu.cmu.tetrad.algcomparison.simulation as sim
import edu.cmu.tetrad.algcomparison.graph as graph

import pytetrad.translate as tr

# An easy way to simulate data in Tetrad is to use the algorithm comparison tool.
# Here's an example.

params = Parameters()

params.set(Params.SAMPLE_SIZE, 1000)
params.set(Params.NUM_MEASURES, 30)
params.set(Params.AVG_DEGREE, 6)
params.set(Params.NUM_LATENTS, 8)
params.set(Params.RANDOMIZE_COLUMNS, True)
params.set(Params.COEF_LOW, 0)
params.set(Params.COEF_HIGH, 1)
params.set(Params.VAR_LOW, 1)
params.set(Params.VAR_HIGH, 3)
params.set(Params.VERBOSE, False)
params.set(Params.NUM_RUNS, 1)

sim_ = sim.SemSimulation(graph.RandomForward())
sim_.createData(params, True)
data_model = sim_.getDataModel(0)
data = tr.tetrad_to_pandas(data_model)

print(data)



