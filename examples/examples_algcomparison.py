import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

from pytetrad.util import startJVM
startJVM()

# This is an example of how ot write and algcomparison script to do algorithm
# comparison in Tetrad. It may not be the best example yet, but it does make
# clear how the script can be written. JR 2023-02-27

import edu.cmu.tetrad.util as tu

import edu.cmu.tetrad.algcomparison as ac

# df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
# df = df.astype({col: "float64" for col in df.columns})

params = tu.Parameters()
params.set(tu.Params.ALPHA, 1e-5, 0.0001, 0.001, 0.01, 0.1)
params.set(tu.Params.PENALTY_DISCOUNT, 1, 2, 4)

params.set(tu.Params.SAMPLE_SIZE, 1000, 10000)
params.set(tu.Params.NUM_MEASURES, 30)
params.set(tu.Params.AVG_DEGREE, 6)
params.set(tu.Params.NUM_LATENTS, 8)
params.set(tu.Params.RANDOMIZE_COLUMNS, True)
params.set(tu.Params.COEF_LOW, 0)
params.set(tu.Params.COEF_HIGH, 1)
params.set(tu.Params.VAR_LOW, 1)
params.set(tu.Params.VAR_HIGH, 3)
params.set(tu.Params.VERBOSE, False)

params.set(tu.Params.NUM_RUNS, 10)

params.set(tu.Params.BOSS_ALG, 1)
params.set(tu.Params.DEPTH, -1)
params.set(tu.Params.MAX_PATH_LENGTH, 2)
params.set(tu.Params.COMPLETE_RULE_SET_USED, True)
params.set(tu.Params.POSSIBLE_DSEP_DONE, True)
params.set(tu.Params.DO_DISCRIMINATING_PATH_TAIL_RULE, True)

# Flags
params.set(tu.Params.GRASP_USE_RASKUTTI_UHLER, False)
params.set(tu.Params.GRASP_USE_SCORE, True)
params.set(tu.Params.GRASP_USE_DATA_ORDER, True)
params.set(tu.Params.NUM_STARTS, 1)

# default
params.set(tu.Params.SEM_GIC_RULE, 4)
params.set(tu.Params.SEM_BIC_STRUCTURE_PRIOR, 3)

params.set(tu.Params.DIFFERENT_GRAPHS, True)

params.set(tu.Params.ADD_ORIGINAL_DATASET, False)

score = ac.score.SemBicScore()
test = ac.independence.FisherZ()

algorithms = ac.algorithm.Algorithms()

algorithms.add(ac.algorithm.oracle.pag.Fci(test))
algorithms.add(ac.algorithm.oracle.pag.Rfci(test))
algorithms.add(ac.algorithm.oracle.pag.GFCI(test, score))
algorithms.add(ac.algorithm.oracle.pag.BFCI(test, score))
algorithms.add(ac.algorithm.oracle.pag.LVSWAP_1(test, score))
algorithms.add(ac.algorithm.oracle.pag.LVSWAP_2a(test, score))
algorithms.add(ac.algorithm.oracle.pag.LVSWAP_2b(test, score))

simulations = ac.simulation.Simulations()
simulations.add(ac.simulation.SemSimulation(ac.graph.RandomForward()))

statistics = ac.statistic.Statistics()
statistics.add(ac.statistic.LegalPag())
statistics.add(ac.statistic.NoAlmostCyclicPathsCondition())
statistics.add(ac.statistic.NoAlmostCyclicPathsInMagCondition())
statistics.add(ac.statistic.NoAlmostCyclicPathsInMagCondition())
statistics.add(ac.statistic.NoCyclicPathsInMagCondition())
statistics.add(ac.statistic.MaximalityCondition())

statistics.add(ac.statistic.ParameterColumn(tu.Params.ALPHA))
statistics.add(ac.statistic.ParameterColumn(tu.Params.PENALTY_DISCOUNT))
statistics.add(ac.statistic.ParameterColumn(tu.Params.SAMPLE_SIZE))
statistics.add(ac.statistic.ParameterColumn(tu.Params.DEPTH))
statistics.add(ac.statistic.ParameterColumn(tu.Params.ZS_RISK_BOUND))
statistics.add(ac.statistic.ParameterColumn(tu.Params.EBIC_GAMMA))

statistics.add(ac.statistic.LegalPag())
statistics.add(ac.statistic.NumDirectedEdges())
statistics.add(ac.statistic.TrueDagPrecisionTails())
statistics.add(ac.statistic.TrueDagPrecisionArrow())
statistics.add(ac.statistic.NumDirectedShouldBePartiallyDirected())
statistics.add(ac.statistic.NumDirectedEdges())
statistics.add(ac.statistic.TrueDagPrecisionTails())
statistics.add(ac.statistic.NumDirectedShouldBePartiallyDirected())
statistics.add(ac.statistic.NumDirectedEdges())
statistics.add(ac.statistic.NumBidirectedEdgesEst())
statistics.add(ac.statistic.BidirectedLatentPrecision())

statistics.add(ac.statistic.AncestorPrecision())
statistics.add(ac.statistic.AncestorRecall())
statistics.add(ac.statistic.AncestorF1())
statistics.add(ac.statistic.SemidirectedPrecision())
statistics.add(ac.statistic.SemidirectedRecall())
statistics.add(ac.statistic.SemidirectedPathF1())
statistics.add(ac.statistic.NoSemidirectedPrecision())
statistics.add(ac.statistic.NoSemidirectedRecall())
statistics.add(ac.statistic.NoSemidirectedF1())

statistics.add(ac.statistic.ElapsedCpuTime())

comparison =ac.Comparison()
comparison.setShowAlgorithmIndices(True)
comparison.setComparisonGraph(ac.Comparison.ComparisonGraph.true_DAG)
comparison.setParallelized(True)

comparison.compareFromSimulations("../testLvSwap", simulations, algorithms, statistics, params)
