## Provides a simple wrapper for many of the Tetrad searches that can be used
## either from Python (for the lazy) or from R. All of the JPype code is
## safely hidden away. The inputs are all pandas data frames
## and the outputs are PCALG-formatted graphs, also data frames. (In a
## future version, we may allow the outputs to be given other formats.)

import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass

import tools.translate as tr
import tools.search as search
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.data as td
import java.lang as lang


class TetradSearch:

    def __init__(self, data):
        self.data = tr.pandas_data_to_tetrad(data)
        self.score = None
        self.test = None
        self.verbose = False
        self.knowledge = td.Knowledge()

    def use_sem_bic(self, penalty_discount=2):
        score = ts.SemBicScore(self.data)
        score.setPenaltyDiscount(penalty_discount)
        self.score = score

    def use_bdeu(self, sample_prior=10, structure_prior=0):
        score = ts.BDeuScore(self.data)
        score.setSamplePrior(sample_prior)
        score.setStructurePrior(structure_prior)
        self.score = score

    def use_conditional_gaussian_score(self, penalty_discount=1, discretize=True, num_categories_to_discretize=3, structure_prior=0):
        score = ts.ConditionalGaussianScore(self.data, penalty_discount, discretize)
        score.setNumCategoriesToDiscretize(num_categories_to_discretize)
        score.setStructurePrior(structure_prior)
        self.score = score

    def use_degenerate_gaussian_score(self, penalty_discount=1, structure_prior=0):
        score = ts.DegenerateGaussianScore(self.data)
        score.setPenaltyDiscount(penalty_discount)
        score.setStructurePrior(structure_prior)
        self.score = score

    def use_fisher_z(self, alpha=0.01):
        test = ts.IndTestFisherZ(self.data, alpha)
        self.test = test

    def use_chi_square(self, alpha=0.01):
        test = ts.IndTestChiSquare(self.data, alpha)
        self.test = test

    def use_g_square(self, alpha=0.01):
        test = ts.IndTestGSquare(self.data, alpha)
        self.test = test

    def use_conditional_gaussian_test(self, alpha=0.01, discretize=True, num_categories_to_discretize=3):
        test = ts.IndTestConditionalGaussianLRT(self.data, alpha, discretize)
        test.setNumCategoriesToDiscretize(num_categories_to_discretize)
        self.test = test

    def use_degenerate_gaussian_test(self, alpha=0.01):
        test = ts.IndTestDegenerateGaussianLRT(self.data)
        test.setAlpha(alpha)
        self.test = test

    def add_to_tier(self, tier, var_name):
        self.knowledge.addToTier(lang.Integer(tier), lang.String(var_name))

    def add_fobidden(self, var_name_1, var_name_2):
        self.knowledge.addForbidden(lang.String(var_name_1), lang.Stringvar_name_2)

    def add_required(self, var_name_1, var_name_2):
        self.knowledge.addRequied(lang.String(var_name_1), lang.Stringvar_name_2)

    def clear_knowledge(self):
        self.knowledge.clear()

    def set_verbose(self, verbose):
        self.verbose = verbose

    def run_fges(self):
        graph = search.fges(self.score, self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_boss(self, depth=-1):
        graph = search.boss(self.score, depth=depth, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_sp(self):
        graph = search.sp(self.score, self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_grasp(self):
        graph = search.grasp(self.score, self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_gango(self):
        graph = search.gango(self.score, self.data, self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_pc(self):
        graph = search.pc(self.test, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_cpc(self):
        graph = search.cpc(self.score, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_pcmax(self):
        graph = search.pcmax(self.score, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_fci(self):
        graph = search.fci(self.test, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_gfci(self):
        graph = search.gfci(self.test, self.score)#//, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_bfci(self):
        graph = search.bfci(self.test, self.score, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_grasp_fci(self):
        graph = search.grasp_fci(self.test, self.score, knowledge=self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_ccd(self):
        if not self.knowledge.isEmpty():
            print("CCD does not use knowledge.")
            return

        graph = search.ccd(self.test)
        return tr.tetrad_graph_to_pcalg(graph)

    def run_svar_fci(self):
        num_lags = 2
        lagged_data = ts.TimeSeriesUtils.createLagData(self.data, num_lags)
        ts_test = ts.IndTestFisherZ(lagged_data, 0.01)
        ts_score = ts.SemBicScore(lagged_data)
        ts_score.setPenaltyDiscount(2)
        svar_fci = ts.SvarGFci(ts_test, ts_score)
        svar_fci.setKnowledge(lagged_data.getKnowledge())
        svar_fci.setVerbose(True)
        svar_fci_graph = svar_fci.search()
        return tr.tetrad_graph_to_pcalg(svar_fci_graph)
