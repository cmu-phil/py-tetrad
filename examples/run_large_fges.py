import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

import jpype
import jpype.imports

jpype.startJVM("-Xmx40g", classpath=[f"{BASE_DIR}/tetrad-gui-7.2.2-launch.jar"])

# Note: This is an example of how to write an algcomparison script to do algorithm
# comparison in Tetrad. It may not be the best example yet, but it does make
# clear how the script can be written. JR 2023-02-27

from edu.cmu.tetrad.util import Params, Parameters

from edu.cmu.tetrad.algcomparison import Comparison
from edu.cmu.tetrad.algcomparison.algorithm import Algorithms
from edu.cmu.tetrad.algcomparison.simulation import Simulations
import edu.cmu.tetrad.algcomparison.simulation as sim
import edu.cmu.tetrad.algcomparison.score as score
import edu.cmu.tetrad.algcomparison.graph as graph
import edu.cmu.tetrad.algcomparison.independence as ind
import edu.cmu.tetrad.algcomparison.statistic as stat
import edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag as cpdag

# df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
# df = df.astype({col: "float64" for col in df.columns})

params = Parameters()
params.set(Params.PENALTY_DISCOUNT, 2)

params.set(Params.SAMPLE_SIZE, 3000)
params.set(Params.NUM_MEASURES, 5000)
params.set(Params.AVG_DEGREE, 2)
params.set(Params.NUM_LATENTS, 0)
params.set(Params.RANDOMIZE_COLUMNS, False)
params.set(Params.COEF_LOW, 0)
params.set(Params.COEF_HIGH, 1)
params.set(Params.VAR_LOW, 1)
params.set(Params.VAR_HIGH, 3)
params.set(Params.FAITHFULNESS_ASSUMED, True)
params.set(Params.PARALLELIZED, True)
params.set(Params.VERBOSE, True)

params.set(Params.NUM_RUNS, 1)

score = score.SemBicScore()
test = ind.FisherZ()

algorithms = Algorithms()

algorithms.add(cpdag.Fges(score))

simulations = Simulations()
simulations.add(sim.SemSimulation(graph.RandomForward()))

statistics = stat.Statistics()

statistics.add(stat.ParameterColumn(Params.NUM_MEASURES))
statistics.add(stat.ParameterColumn(Params.SAMPLE_SIZE))
statistics.add(stat.AdjacencyPrecision())
statistics.add(stat.AdjacencyRecall())
statistics.add(stat.ArrowheadPrecision())
statistics.add(stat.ArrowheadRecall())

statistics.add(stat.ElapsedCpuTime())

comparison = Comparison()
comparison.setShowAlgorithmIndices(True)
comparison.setComparisonGraph(Comparison.ComparisonGraph.true_DAG)
comparison.setParallelized(True)

comparison.compareFromSimulations("../testFges", simulations, algorithms, statistics, params)
