import sys
import jpype.imports

BASE_DIR = ".."
sys.path.append(BASE_DIR)
jpype.startJVM(classpath=[f"{BASE_DIR}/pytetrad/resources/tetrad-current.jar"])

import edu.cmu.tetrad.algcomparison.simulation as sim
import edu.cmu.tetrad.algcomparison.graph as ag
import edu.cmu.tetrad.search as search
import edu.cmu.tetrad.graph as graph
import edu.cmu.tetrad.algcomparison.independence as ind
import edu.cmu.tetrad.algcomparison.statistic as st
from edu.cmu.tetrad.util import Params, Parameters

num_measures = 20
avg_degree = 4
sample_size = 1000
num_starts = 3
alpha = 0.01
markov_alpha = 0.05

penalties = [10, 8, 6, 5, 4, 3.5, 3, 2.5, 2, 1.75, 1.5, 1.25, 1, 0.5]
alphas = [0.001, 0.01, 0.05, 0.1]

params = Parameters()
params.set(Params.ALPHA, alpha)
params.set(Params.NUM_MEASURES, num_measures)
params.set(Params.AVG_DEGREE, avg_degree)
params.set(Params.SAMPLE_SIZE, sample_size)
params.set(Params.NUM_STARTS, num_starts)

# paramValue is a range of values for the parameter being used. For score-based
# algorithms it will be penalty discount; for constraint-based it will be alpha.
def markov_check(graph, data, params):
    test = ind.FisherZ().getTest(data, params)
    mc = search.MarkovCheck(graph, test, search.ConditioningSetType.LOCAL_MARKOV)
    mc.setPercentResample(.7)
    mc.generateResults()
    p_ad = mc.getAndersonDarlingP(True)
    p_ks = mc.getKsPValue(True)
    p_b = mc.getBinomialPValue(True)
    fd_indep = mc.getFractionDependent(True)
    fd_dep = mc.getFractionDependent(False)
    return p_ad, p_ks, p_b, fd_indep, fd_dep

def accuracy(true_graph, est_graph, data):
    est_graph = graph.GraphUtils.replaceNodes(est_graph, true_graph.getNodes())
    ap = st.AdjacencyPrecision().getValue(true_graph, est_graph, data)
    ar = st.AdjacencyRecall().getValue(true_graph, est_graph, data)
    ahp = st.ArrowheadPrecision().getValue(true_graph, est_graph, data)
    ahr = st.ArrowheadRecall().getValue(true_graph, est_graph, data)
    return ap, ar, ahp, ahr

def getData(params):
    _sim = sim.SemSimulation(ag.RandomForward())
    _sim.createData(params, False)
    data = _sim.getDataModel(0)
    graph = _sim.getTrueGraph(0)
    return data, graph

def tableLine():
    data, graph = getData(params)
    ap, ar, ahp, ahr = accuracy(graph, graph, data)
    p_ad, p_ks, p_b, fd_indep, fd_dep = markov_check(graph, data, params)
    edges = graph.getNumEdges()

    return p_ad, p_b, edges, f"true_dag  {num_measures:5}   {avg_degree:5} " \
         f"  {p_ad:.3f} {p_b:.3f}  " \
         f" {fd_indep:1.3f}   {fd_dep:.3f}    {edges:3}  " \
         f"{ap:.3f} {ar:.3f} {ahp:.3f} {ahr:.3f}"

print('alg = the chosen algorithm')
print('nodes = # of measured nodes in the graph')
print('avgdeg = average degree of the graph')
print('param = penalty discount of the SEM BIC score, where used, or alpha for Fisher Z, where used')
print('p_ad = p-value of the Anderson Darling test of Uniformity')
print('p_b = p-value of the Binomial of whether # dependencies are in bounds')
print('fd_ind = fraction of dependencies for dsep(x, y | parents(x) implied by the estimated cpdag')
print('fd_dep = fraction of dependencies for dconn(x, y | parents(x) implied by the estimated cpdag')
print('edges = # edges in the estimated graph')
print('ap = adjacency precision')
print('ar = adjacency recall')
print()

header = f"graph     nodes  avgdeg    p_ad   p_b  fd_ind  fd_dep  edges     ap    ar   ahp   ahr"

print(header)

print('-' * 85)

for i in range(0, 100):
    p_ad, p_b, edges, line = tableLine()
    print(line)

