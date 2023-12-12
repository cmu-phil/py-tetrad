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
import random
import math

## This script tries to pick a good model from a list of models. Various rules are tried.
## jdramsey 2023-12-11

class EstimateGoodModel:
    def __init__(self, num_measures, density, sample_size):
        self.__num_measures = num_measures
        self.__density = density
        self.__sample_size = sample_size
        self.__avg_degree = math.floor(density * num_measures)
        self.__num_starts = 2
        self.__ind_test_alpha = 0.01
        self.__markov_alpha_b = 0.05
        self.__markov_alpha_ad = 0.05
        self.__penalties = [10, 8, 6, 5, 4, 3.5, 3, 2.5, 2, 1.75, 1.5, 1.25, 1, 0.5]
        self.__alphas = [0.001, 0.01, 0.05, 0.1]
        self.__percentResample = 0.5

        self.__params = Parameters()
        self.__params.set(Params.ALPHA, self.__ind_test_alpha)
        self.__params.set(Params.NUM_MEASURES, self.__num_measures)
        self.__params.set(Params.AVG_DEGREE, self.__avg_degree)
        self.__params.set(Params.SAMPLE_SIZE, self.__sample_size)
        self.__params.set(Params.NUM_STARTS, self.__num_starts)

        self.__fd_dep = 0
        self.__fd_indep = 0

        self.__min_edges_ad = 100000
        self.__best_lines_ad = []

        self.__max_fd_dep_ad2 = -1
        self.__best_lines_ad2 = []

        self.__min_edges_b = 100000
        self.__best_lines_b = []

        self.__max_fd_dep_b2 = -1
        self.__best_lines_b2 = []

        self.__max_fd_diff = -1
        self.__best_lines_max_diff = []

        self.__max_fd_diff = 0

    # paramValue is a range of values for the parameter being used. For score-based
    # algorithms it will be penalty discount; for constraint-based it will be alpha.
    def getGraph(self, alg, paramValue, data):
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
        elif alg == 'cpc':
            _search.use_fisher_z(paramValue)
            _search.run_cpc()

        return _search.get_java()

    def markov_check(self, graph, data, params):
        test = ind.FisherZ().getTest(data, params)
        mc = search.MarkovCheck(graph, test, search.ConditioningSetType.LOCAL_MARKOV)
        mc.setPercentResammple(self.__percentResample)
        mc.generateResults()
        p_ad = mc.getAndersonDarlingP(True)
        p_ks = mc.getKsPValue(True)
        p_b = mc.getBinomialPValue(True)
        fd_indep = mc.getFractionDependent(True)
        fd_dep = mc.getFractionDependent(False)
        num_tests_indep = mc.getNumTests(True)
        num_test_dep = mc.getNumTests(False)
        return p_ad, p_ks, p_b, fd_indep, fd_dep, num_tests_indep, num_test_dep

    def accuracy(self, true_graph, est_graph, data):
        est_graph = graph.GraphUtils.replaceNodes(est_graph, true_graph.getNodes())
        cpdag = graph.GraphTransforms.cpdagForDag(true_graph)
        ap = st.AdjacencyPrecision().getValue(cpdag, est_graph, data)
        ar = st.AdjacencyRecall().getValue(cpdag, est_graph, data)
        ahp = st.ArrowheadPrecision().getValue(cpdag, est_graph, data)
        ahr = st.ArrowheadRecall().getValue(cpdag, est_graph, data)
        return ap, ar, ahp, ahr

    def getData(self, params):
        _sim = sim.SemSimulation(ag.RandomForward())
        _sim.createData(params, False)
        data = _sim.getDataModel(0)
        graph = _sim.getTrueGraph(0)
        return data, graph

    def tableLine(self, alg, param):
        global num_test_indep
        data, _graph = self.getData(self.__params)
        cpdag = self.getGraph(alg, param, data)
        ap, ar, ahp, ahr = self.accuracy(_graph, cpdag, data)

        num_checks = 10

        p_ad = 1.0
        p_ks = 1.0
        p_b = 1.0
        fd_indep = 10000
        fd_dep = 10000
        num_test_indep = 0
        num_test_dep = 0

        for i in range(0, num_checks):
            _p_ad, _p_ks, _p_b, _fd_indep, _fd_dep, num_test_indep, num_test_dep \
                = self.markov_check(cpdag, data, self.__params)

            if (_p_ad < p_ad): p_ad = _p_ad
            if (_p_ks < p_ks): p_ks = _p_ks
            if (_p_b < p_b): p_b = _p_b
            if (_fd_indep < fd_indep): fd_indep = _fd_indep
            if (_fd_dep < fd_dep): fd_dep = _fd_dep

        if (fd_indep == 10000): fd_indep = 0
        if (fd_dep == 10000): fd_dep = 0

        edges = cpdag.getNumEdges()

        # cpdag_density = cpdag.getNumEdges() / (cpdag.getNumNodes() * cpdag.getNumNodes() - 1) / 2

        line = f"{alg:6} {num_measures:5}   {self.__avg_degree:5} {param:8.3f}  " \
               f" {p_ad:.3f} {p_b:.3f}  " \
               f" {fd_indep:1.3f}   {fd_dep:.3f}    {edges:3}  " \
               f"{ap:.3f} {ar:.3f} {ahp:.3f} {ahr:.3f} {num_test_indep:3} {num_test_dep:3}"

        return p_ad, p_b, fd_indep, fd_dep, edges, line
        #
        # return p_ad, p_b, fd_indep, fd_dep, edges, f"{alg:6} {cpdag_density:5.2f}   {0:5} {param:8.3f}  " \
        #      f" {p_ad:.3f} {p_b:.3f}  " \
        #      f" {fd_indep:1.3f}   {fd_dep:.3f}    {edges:3}  " \
        #      f"{ap:.3f} {ar:.3f} {ahp:.3f} {ahr:.3f}"

    def saveBestLines(self, alg, params):
        for param in params:
            p_ad, p_b, fd_indep, fd_dep, edges, line = self.tableLine(alg, param)
            print(line)
            self.rule1(edges, line, p_ad)
            self.rule2(fd_dep, line, p_ad)
            self.rule3(edges, line, p_b)
            self.rule4(fd_dep, line, p_b)
            self.rule5(fd_dep, fd_indep, line, p_ad, p_b)

    def rule1(self, edges, line, p_ad):
        if p_ad >= self.__markov_alpha_ad:
            if edges == self.__min_edges_ad:
                self.__best_lines_ad.append(line)
            elif edges < self.__min_edges_ad:
                self.__min_edges_ad = edges
                self.__best_lines_ad = []
                self.__best_lines_ad.append(line)

    def rule2(self, fd_dep, line, p_ad):
        if p_ad >= self.__markov_alpha_ad:
            if fd_dep == self.__max_fd_dep_ad2:
                self.__best_lines_ad2.append(line)
            elif fd_dep > self.__max_fd_dep_ad2:
                self.__max_fd_dep_ad2 = fd_dep
                self.__best_lines_ad2 = []
                self.__best_lines_ad2.append(line)

    def rule3(self, edges, line, p_b):
        if p_b > self.__markov_alpha_b:
            if edges == self.__min_edges_b:
                self.__best_lines_b.append(line)
            elif edges < self.__min_edges_b:
                self.__min_edges_b = edges
                self.__best_lines_b = []
                self.__best_lines_b.append(line)

    def rule4(self, fd_dep, line, p_b):
        if p_b > self.__markov_alpha_b:
            if fd_dep == self.__max_fd_dep_b2:
                self.__best_lines_b2.append(line)
            elif fd_dep > self.__max_fd_dep_b2:
                self.__max_fd_dep_b2 = fd_dep
                self.__best_lines_b2 = []
                self.__best_lines_b2.append(line)

    def rule5(self, fd_dep, fd_indep, line, p_ad, p_b):
        if p_ad >= self.__markov_alpha_ad and p_b > self.__markov_alpha_b:
            max_fd_diff = fd_dep - fd_indep
            if (max_fd_diff == self.__max_fd_diff):
                self.__best_lines_max_diff.append(line)
            if (max_fd_diff > self.__max_fd_diff):
                self.__max_fd_diff = max_fd_diff
                self.__best_lines_max_diff = []
                self.__best_lines_max_diff.append(line)

    def header(self):
        print(f"alg    nodes  avgdeg    param    p_ad   p_b  fd_ind  fd_dep  edges     ap    ar   ahp   ahr")
        print('-' * 91)

    def printInfo(self, msg):
        print()
        print()
        print(msg)
        print()

    def printLines(self, lines):
        self.header()
        for _line in lines:
            print(_line)

    def printParameterDefs(self):
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

    def get_alphas(self):
        return self.__alphas

    def get_penalties(self):
        return self.__penalties

    def get_best_lines_ad(self):
        return self.__best_lines_ad

    def get_best_lines_ad2(self):
        return self.__best_lines_ad2

    def get_best_lines_b(self):
        return self.__best_lines_b

    def get_best_lines_b2(self):
        return self.__best_lines_b2

    def get_best_lines_max_diff(self):
        return self.__best_lines_max_diff


### This runs it... ###

num_measures = random.randint(9, 30)
density = random.uniform(0.1, 0.5)
sample_size = 1000

est = EstimateGoodModel(num_measures, density, sample_size)

est.printParameterDefs()
est.header()

est.saveBestLines('pc', est.get_alphas())
est.saveBestLines('cpc', est.get_alphas())
est.saveBestLines('fges', est.get_penalties())
est.saveBestLines('grasp', est.get_penalties())
est.saveBestLines('boss', est.get_penalties())

est.printInfo('Best choices for the AD Plus Min Edges:')
est.printLines(est.get_best_lines_ad())

# est.printInfo('Best choices for the Anderson Darling + Max fd_dep rule:')
# est.printLines(est.get_best_lines_ad2())

est.printInfo('Best choices for the Binomial plus Min Edges:')
est.printLines(est.get_best_lines_b())

est.printInfo('Best choices for the Binomial + Max fd_dep rule:')
est.printLines(est.get_best_lines_b2())

# est.printInfo('Best choices for the Markov + Max Diff rule:')
# est.printLines(est.get_best_lines_max_diff())
