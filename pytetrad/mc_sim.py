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

import tools.TetradSearch as ts
import tools.translate as tr

num_measures = 20
avg_degree = 4
sample_size = 1000
num_starts = 2
ind_test_alpha = 0.01
markov_alpha_b = 0.01
markov_alpha_ad = 0.01

penalties = [10, 8, 6, 5, 4, 3.5, 3, 2.5, 2, 1.75, 1.5, 1.25, 1, 0.5]
alphas = [0.001, 0.01, 0.05, 0.1]

params = Parameters()
params.set(Params.ALPHA, ind_test_alpha)
params.set(Params.NUM_MEASURES, num_measures)
params.set(Params.AVG_DEGREE, avg_degree)
params.set(Params.SAMPLE_SIZE, sample_size)
params.set(Params.NUM_STARTS, num_starts)

# paramValue is a range of values for the parameter being used. For score-based
# algorithms it will be penalty discount; for constraint-based it will be alpha.
def getGraph(alg, paramValue, data):
    _to_pandas = tr.tetrad_data_to_pandas(data)
    _to_pandas = _to_pandas.astype({col: "float64" for col in _to_pandas.columns})
    _search = ts.TetradSearch(_to_pandas)
    _search.set_verbose(False)
    _search.use_sem_bic(penalty_discount=paramValue)

    if alg == 'fges':
        _search.use_sem_bic(penalty_discount=paramValue)
        _search.run_fges(faithfulness_assumed=False)
    elif alg == 'boss':
        _search.use_sem_bic(penalty_discount=paramValue)
        _search.run_boss()
    elif alg == 'grasp':
        _search.use_sem_bic(penalty_discount=paramValue)
        _search.use_fisher_z(0.05)
        _search.run_grasp()
    elif alg == 'pc':
        _search.use_fisher_z(paramValue)
        _search.run_pc()

    return _search.get_java()

def markov_check(graph, data, params):
    test = ind.FisherZ().getTest(data, params)
    mc = search.MarkovCheck(graph, test, search.ConditioningSetType.LOCAL_MARKOV)
    mc.setPercentResammple(.5)
    mc.generateResults()
    p_ad = mc.getAndersonDarlingP(True)
    p_ks = mc.getKsPValue(True)
    p_b = mc.getBinomialPValue(True)
    fd_indep = mc.getFractionDependent(True)
    fd_dep = mc.getFractionDependent(False)
    return p_ad, p_ks, p_b, fd_indep, fd_dep

def accuracy(true_graph, est_graph, data):
    est_graph = graph.GraphUtils.replaceNodes(est_graph, true_graph.getNodes())
    cpdag = graph.GraphTransforms.cpdagForDag(true_graph)
    ap = st.AdjacencyPrecision().getValue(cpdag, est_graph, data)
    ar = st.AdjacencyRecall().getValue(cpdag, est_graph, data)
    ahp = st.ArrowheadPrecision().getValue(cpdag, est_graph, data)
    ahr = st.ArrowheadRecall().getValue(cpdag, est_graph, data)
    return ap, ar, ahp, ahr

def getData(params):
    _sim = sim.SemSimulation(ag.RandomForward())
    _sim.createData(params, False)
    data = _sim.getDataModel(0)
    graph = _sim.getTrueGraph(0)
    return data, graph

def tableLine(alg, param):
        data, _graph = getData(params)
        cpdag = getGraph(alg, param, data)
        ap, ar, ahp, ahr = accuracy(_graph, cpdag, data)

        num_checks = 1

        p_ad = 0
        p_ks = 0
        p_b = 0
        fd_indep = 0
        fd_dep = 0

        for i in range(0, num_checks):
            _p_ad, _p_ks, _p_b, _fd_indep, _fd_dep = markov_check(cpdag, data, params)
            p_ad += _p_ad
            p_ks += _p_ks
            p_b = _p_b
            fd_indep += _fd_indep
            fd_dep += _fd_dep

        p_ad /= num_checks
        p_ks /= num_checks
        p_b /= num_checks
        fd_indep /= num_checks
        fd_dep /= num_checks

        edges = cpdag.getNumEdges()

        return p_ad, p_b, fd_indep, fd_dep, edges, f"{alg:6} {num_measures:5}   {avg_degree:5} {param:8.3f}  " \
             f" {p_ad:.3f} {p_b:.3f}  " \
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

header = f"alg    nodes  avgdeg    param    p_ad   p_b  fd_ind  fd_dep  edges     ap    ar   ahp   ahr"

print(header)

print('-' * 91)

min_edges_ad = 100000
best_lines_ad = []

max_fd_dep_ad2 = -1
best_lines_ad2 = []

min_edges_b = 100000
best_lines_b = []

max_fd_dep_b2 = -1
best_lines_b2 = []

min_fd_indep = 1
max_fd_dep = 0
best_lines_max_diff = []


for param in alphas:
    p_ad, p_b, fd_indep, fd_dep, edges, line = tableLine('pc', param)
    print(line)
    if p_ad > markov_alpha_ad:
        if edges == min_edges_ad:
            best_lines_ad.append(line)
        elif edges < min_edges_ad:
            min_edges_ad = edges
            best_lines_ad = []
            best_lines_ad.append(line)
    if p_ad > markov_alpha_ad:
        if fd_dep == max_fd_dep_ad2:
            best_lines_ad2.append(line)
        elif fd_dep > max_fd_dep_ad2:
            max_fd_dep_ad2 = fd_dep
            best_lines_ad2 = []
            best_lines_ad2.append(line)
    if p_b > markov_alpha_b :
        if edges == min_edges_b:
            best_lines_b.append(line)
        elif edges < min_edges_b:
            min_edges_b = edges
            best_lines_b = []
            best_lines_b.append(line)
    if p_b > markov_alpha_b:
        if fd_dep == max_fd_dep_b2:
            best_lines_b2.append(line)
        elif fd_dep > max_fd_dep_b2:
            max_fd_dep_b2 = fd_dep
            best_lines_b2 = []
            best_lines_b2.append(line)
    if (fd_indep < min_fd_indep):
        min_fd_indep = fd_indep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)
    if (fd_dep > max_fd_dep):
        max_fd_dep = fd_dep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)

for param in penalties:
    p_ad, p_b, fd_indep, fd_dep, edges, line = tableLine('fges', param)
    print(line)
    if p_ad > markov_alpha_ad:
        if edges == min_edges_ad:
            best_lines_ad.append(line)
        elif edges < min_edges_ad:
            min_edges_ad = edges
            best_lines_ad = []
            best_lines_ad.append(line)
    if p_ad > markov_alpha_ad:
        if fd_dep == max_fd_dep_ad2:
            best_lines_ad2.append(line)
        elif fd_dep > max_fd_dep_ad2:
            max_fd_dep_ad2 = fd_dep
            best_lines_ad2 = []
            best_lines_ad2.append(line)
    if p_b > markov_alpha_b :
        if edges == min_edges_b:
            best_lines_b.append(line)
        elif edges < min_edges_b:
            min_edges_b = edges
            best_lines_b = []
            best_lines_b.append(line)
    if p_b > markov_alpha_b:
        if fd_dep == max_fd_dep_b2:
            best_lines_b2.append(line)
        elif fd_dep > max_fd_dep_b2:
            max_fd_dep_b2 = fd_dep
            best_lines_b2 = []
            best_lines_b2.append(line)
    if (fd_indep < min_fd_indep):
        min_fd_indep = fd_indep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)
    if (fd_dep > max_fd_dep):
        max_fd_dep = fd_dep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)

for param in penalties:
    p_ad, p_b, fd_indep, fd_dep, edges, line = tableLine('grasp', param)
    print(line)
    if p_ad > markov_alpha_ad:
        if edges == min_edges_ad:
            best_lines_ad.append(line)
        elif edges < min_edges_ad:
            min_edges_ad = edges
            best_lines_ad = []
            best_lines_ad.append(line)
    if p_ad > markov_alpha_ad:
        if fd_dep == max_fd_dep_ad2:
            best_lines_ad2.append(line)
        elif fd_dep > max_fd_dep_ad2:
            max_fd_dep_ad2 = fd_dep
            best_lines_ad2 = []
            best_lines_ad2.append(line)
    if p_b > markov_alpha_b :
        if edges == min_edges_b:
            best_lines_b.append(line)
        elif edges < min_edges_b:
            min_edges_b = edges
            best_lines_b = []
            best_lines_b.append(line)
    if p_b > markov_alpha_b:
        if fd_dep == max_fd_dep_b2:
            best_lines_b2.append(line)
        elif fd_dep > max_fd_dep_b2:
            max_fd_dep_b2 = fd_dep
            best_lines_b2 = []
            best_lines_b2.append(line)
    if (fd_indep < min_fd_indep):
        min_fd_indep = fd_indep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)
    if (fd_dep > max_fd_dep):
        max_fd_dep = fd_dep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)

for param in penalties:
    p_ad, p_b, fd_indep, fd_dep, edges, line = tableLine('boss', param)
    print(line)
    if p_ad > markov_alpha_ad:
        if edges == min_edges_ad:
            best_lines_ad.append(line)
        elif edges < min_edges_ad:
            min_edges_ad = edges
            best_lines_ad = []
            best_lines_ad.append(line)
    if p_ad > markov_alpha_ad:
        if fd_dep == max_fd_dep_ad2:
            best_lines_ad2.append(line)
        elif fd_dep > max_fd_dep_ad2:
            max_fd_dep_ad2 = fd_dep
            best_lines_ad2 = []
            best_lines_ad2.append(line)
    if p_b > markov_alpha_b :
        if edges == min_edges_b:
            best_lines_b.append(line)
        elif edges < min_edges_b:
            min_edges_b = edges
            best_lines_b = []
            best_lines_b.append(line)
    if p_b > markov_alpha_b:
        if fd_dep == max_fd_dep_b2:
            best_lines_b2.append(line)
        elif fd_dep > max_fd_dep_b2:
            max_fd_dep_b2 = fd_dep
            best_lines_b2 = []
            best_lines_b2.append(line)
    if (fd_indep < min_fd_indep):
        min_fd_indep = fd_indep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)
    if (fd_dep > max_fd_dep):
        max_fd_dep = fd_dep
        best_lines_max_diff = []
        best_lines_max_diff.append(line)

print()
print()
print('Best choices for the Binomial plus Min Edges:')
print()
print(header)
print('-' * 91)

for _line in best_lines_b:
    print(_line)

print()
print()
print('Best choices for the AD Plus Min Edges:')
print()
print(header)
print('-' * 91)

for _line in best_lines_ad:
    print(_line)

print()
print()
print('Best choices for the Anderson Darling + Max fd_dep rule:')
print()
print(header)
print('-' * 91)

for _line in best_lines_ad2:
    print(_line)

print()
print()
print('Best choices for the Binomial + Max fd_dep rule:')
print()
print(header)
print('-' * 91)

for _line in best_lines_b2:
    print(_line)

print()
print()
print('Best choices for the Max Diff rule:')
print()
print(header)
print('-' * 91)

for _line in best_lines_max_diff:
    print(_line)