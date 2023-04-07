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
import edu.cmu.tetrad.graph.GraphPersistence as gp
import java.lang as lang


class TetradSearch:

    def __init__(self, data):
        self.data = tr.pandas_data_to_tetrad(data)
        self.score = None
        self.test = None
        self.java = None
        self.verbose = False
        self.knowledge = td.Knowledge()

    def __str__(self):
        display = [self.score, self.test, self.knowledge, self.java]
        return "\n\n".join([str(item) for item in display])
        
    # Maybe add this functionality later
    # def set_data(self, data):
    #     self.data = tr.pandas_data_to_tetrad(data)

    def use_sem_bic(self, penalty_discount=2):
        score = ts.SemBicScore(self.data)
        score.setPenaltyDiscount(penalty_discount)
        self.score = score

    def use_ebic(self, gamma=0.8):
        score = ts.EbicScore(self.data)
        score.setGamma(gamma)
        self.score = score

    def use_kim_score(self, rule_type=4, penalty_discount=2):
        score = ts.KimEtAlScores(self.data)
        score.setRuleType(rule_type)
        score.setPenaltyDiscount(penalty_discount)
        self.score = score

    def use_mixed_variable_polynomial(self, structure_prior=0, f_degree=0, discretize=False):
        score = ts.MVPScore(self.data, structure_prior, f_degree, discretize)
        self.score = score

    def use_poisson_prior(self, lambda_=2):
        score = ts.PoissonPriorScore(self.data)
        score.setLambda(lambda_)
        self.score = score

    def use_zhang_shen_bound(self, risk_bound=0.2):
        score = ts.ZhangShenBoundScore(self.data)
        score.setRiskBound(risk_bound)
        self.score = score

    def use_bdeu(self, sample_prior=10, structure_prior=0):
        score = ts.BDeuScore(self.data)
        score.setSamplePrior(sample_prior)
        score.setStructurePrior(structure_prior)
        self.score = score

    def use_conditional_gaussian_score(self, penalty_discount=1, discretize=True, num_categories_to_discretize=3,
                                       structure_prior=0):
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

    def use_probabilistic_test(self, threshold=False, cutoff=0.5, prior_ess=10):
        test = ts.IndTestProbabilistic(self.data)
        test.setThreshold(threshold)
        test.setCutoff(cutoff)
        test.setPriorEquivalentSampleSize(prior_ess)
        self.test = test

    def use_kci(self, alpha=0.01, approximate=True, width_multipler=1, num_bootstraps=5000, threshold=0.001,
                epsilon=0.001):
        test = ts.Kci(self.data, alpha)
        test.setApproximate(approximate)
        test.setWidthMultiplier(width_multipler)
        test.setNumBootstraps(num_bootstraps)
        test.setThreshold(threshold)
        test.setEpsilon(epsilon)
        self.test = test

    def add_to_tier(self, tier, var_name):
        self.knowledge.addToTier(lang.Integer(tier), lang.String(var_name))

    def add_fobidden(self, var_name_1, var_name_2):
        self.knowledge.addForbidden(lang.String(var_name_1), lang.String(var_name_2))

    def add_required(self, var_name_1, var_name_2):
        self.knowledge.addRequired(lang.String(var_name_1), lang.String(var_name_2))

    def clear_knowledge(self):
        self.knowledge.clear()
    
    def print_knowledge(self): 
        return str(self.knowledge)

    def set_verbose(self, verbose):
        self.verbose = verbose

    def run_fges(self):
        self.java = search.fges(self.score, self.knowledge, verbose=self.verbose)

    def run_boss(self, depth=-1):
        self.java = search.boss(self.score, depth=depth, knowledge=self.knowledge, verbose=self.verbose)

    def run_sp(self):
        self.java = search.sp(self.score, self.knowledge, verbose=self.verbose)

    def run_grasp(self):
        self.java = search.grasp(self.score, self.knowledge, verbose=self.verbose)

    def run_gango(self):
        self.java = search.gango(self.score, self.data, self.knowledge, verbose=self.verbose)

    def run_pc(self):
        self.java = search.pc(self.test, knowledge=self.knowledge, verbose=self.verbose)

    def run_cpc(self):
        self.java = search.cpc(self.score, knowledge=self.knowledge, verbose=self.verbose)

    def run_pcmax(self):
        self.java = search.pcmax(self.score, knowledge=self.knowledge, verbose=self.verbose)

    def run_fci(self):
        self.java = search.fci(self.test, knowledge=self.knowledge, verbose=self.verbose)

    def run_gfci(self):
        self.java = search.gfci(self.test, self.score)  # //, knowledge=self.knowledge, verbose=self.verbose)

    def run_bfci(self):
        self.java = search.bfci(self.test, self.score, knowledge=self.knowledge, verbose=self.verbose)

    def run_grasp_fci(self):
        self.java = search.grasp_fci(self.test, self.score, knowledge=self.knowledge, verbose=self.verbose)

    def run_spfci(self):
        self.java = search.spfci(self.test, self.score, knowledge=self.knowledge, verbose=self.verbose)

    def run_ccd(self):
        if not self.knowledge.isEmpty():
            print("CCD does not use knowledge.")
            return

        self.java = search.ccd(self.test)

    def run_svar_fci(self):
        num_lags = 2
        lagged_data = ts.TimeSeriesUtils.createLagData(self.data, num_lags)
        ts_test = ts.IndTestFisherZ(lagged_data, 0.01)
        ts_score = ts.SemBicScore(lagged_data)
        ts_score.setPenaltyDiscount(2)
        svar_fci = ts.SvarGFci(ts_test, ts_score)
        svar_fci.setKnowledge(lagged_data.getKnowledge())
        svar_fci.setVerbose(True)
        self.java = svar_fci.search()

    def get_data(self): 
        return self.data

    def get_score(self): 
        return self.score

    def get_test(self): 
        return self.test

    def get_verbose(self): 
        return self.verbose

    def get_knowledge(self): 
         return self.knowledge

    def get_java(self): 
        return self.java

    def get_string(self): 
        return lang.String @ self.java.toString()

    def get_causal_learn(self): 
        return tr.tetrad_graph_to_causal_learn(self.java)

    def get_pcalg(self): 
        return tr.tetrad_graph_to_pcalg(self.java)

    def get_dot(self): 
        return str(gp.graphToDot(self.java))

    def get_xml(self): 
        return gp.graphToXml(self.java)
    
    def get_lavaan(self): 
        return gp.graphToLavaan(self.java)
