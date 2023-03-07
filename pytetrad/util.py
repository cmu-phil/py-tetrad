import os
import sys

import jpype
import jpype.imports

from edu.cmu.tetrad.util import Params, Parameters
import edu.cmu.tetrad.algcomparison.simulation as sim
import edu.cmu.tetrad.algcomparison.graph as graph
import pytetrad.translate as tr


# def startJVM():
#     BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
#     sys.path.append(BASE_DIR)
#
#     try:
#         jpype.startJVM(classpath=[f"{BASE_DIR}/tetrad-gui-7.2.2-launch.jar"])
#     except OSError:
#         print("JVM already started")

# Simuolates a continuous dataset with the given arguments and returns the dataset as a pandas dataframe
# along with the graph as a causal-learn GeneralGraph.
def simulateContinuous(num_meas = 20, num_lat = 0, avg_deg = 4, samp_size = 200, coef_low = 0, coef_high = 1, var_low = 1, var_high = 3):
    # Set the parameters for the simulation
    params = Parameters()

    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.NUM_MEASURES, num_meas)
    params.set(Params.AVG_DEGREE, avg_deg)
    params.set(Params.NUM_LATENTS, num_lat)
    params.set(Params.RANDOMIZE_COLUMNS, False)
    params.set(Params.COEF_LOW, coef_low)
    params.set(Params.COEF_HIGH, coef_high)
    params.set(Params.VAR_LOW, var_low)
    params.set(Params.VAR_HIGH, var_high)
    params.set(Params.VERBOSE, False)
    params.set(Params.NUM_RUNS, 1)
    # params.set(Params.SEED, 29483)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.LinearFisherModel(graph.RandomForward())
    sim_.createData(params, True)
    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    D_ = tr.tetrad_to_pandas(D)
    G_ = tr.tetrad_graph_to_causal_learn(G)

    return D_, G_

# Simuolates a discrete dataset with the given arguments and returns the dataset as a pandas dataframe
# along with the graph as a causal-learn GeneralGraph.
def simulateDiscrete(num_meas = 20, num_lat = 0, avg_deg = 4, min_cat=3, max_cat=3, samp_size=1000):
    # Set the parameters for the simulation
    # Set the parameters for the simulation
    params = Parameters()

    # Params for graph
    params.set(Params.NUM_MEASURES, num_meas)
    params.set(Params.NUM_LATENTS, num_lat)
    params.set(Params.AVG_DEGREE, avg_deg)

    # Params for Bayes PM
    params.set(Params.MIN_CATEGORIES, min_cat)
    params.set(Params.MAX_CATEGORIES, max_cat)

    # Params for simuulation
    params.set(Params.RANDOMIZE_COLUMNS, False)
    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.SAVE_LATENT_VARS, False)
    # params.set(Params.SEED, 29483)

    params.set(Params.NUM_RUNS, 1)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.BayesNetSimulation(graph.RandomForward())
    sim_.createData(params, True)
    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    D_ = tr.tetrad_to_pandas(D)
    G_ = tr.tetrad_graph_to_causal_learn(G)

    return D_, G_