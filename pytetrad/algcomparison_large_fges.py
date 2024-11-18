
# Note: This is an example of how to write an algcomparison script to do algorithm
# comparison in Tetrad. It may not be the best example yet, but it does make
# clear how the script can be written. JR 2023-02-27

import jpype.imports

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

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

params = Parameters()
params.set(Params.PENALTY_DISCOUNT, 8)

params.set(Params.SAMPLE_SIZE, 500)
params.set(Params.NUM_MEASURES, 2000)
# params.set(Params.NUM_MEASURES, 20000)
params.set(Params.AVG_DEGREE, 6)
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
simulations.add(sim.LinearFisherModel(graph.RandomForward()))

statistics = stat.Statistics()

statistics.add(stat.ParameterColumn(Params.NUM_MEASURES))
statistics.add(stat.ParameterColumn(Params.SAMPLE_SIZE))
statistics.add(stat.AdjacencyPrecision())
statistics.add(stat.AdjacencyRecall())
statistics.add(stat.ArrowheadPrecision())
statistics.add(stat.ArrowheadRecall())

statistics.add(stat.ElapsedCpuTime())

comparison = Comparison()
comparison.setComparisonGraph(Comparison.ComparisonGraph.true_DAG)

comparison.compareFromSimulations("../testFges", simulations, algorithms, statistics, params)
