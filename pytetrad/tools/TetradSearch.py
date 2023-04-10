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
import edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag as cpdag
import edu.cmu.tetrad.algcomparison.algorithm.oracle.pag as pag

import edu.cmu.tetrad.algcomparison.score as score_
import edu.cmu.tetrad.algcomparison.independence as ind_

from edu.cmu.tetrad.util import Params, Parameters


class TetradSearch:

    def __init__(self, data):
        self.data = tr.pandas_data_to_tetrad(data)
        self.score = None
        self.test = None
        self.java = None
        self.verbose = False
        self.knowledge = td.Knowledge()
        self.params = Parameters()

    def __str__(self):
        display = [self.score, self.test, self.knowledge, self.java]
        return "\n\n".join([str(item) for item in display])

    # Maybe add this functionality later
    # def set_data(self, data):
    #     self.data = tr.pandas_data_to_tetrad(data)

    def use_sem_bic(self, penalty_discount=2, structurePrior=0, sem_bic_rule=1):
        score = ts.SemBicScore(self.data)
        score.setPenaltyDiscount(penalty_discount)
        self.score = score

        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.SEM_BIC_STRUCTURE_PRIOR, structurePrior)
        self.params.set(Params.SEM_BIC_RULE, sem_bic_rule)
        self.SCORE = score_.SemBicScore()

    def use_ebic(self, gamma=0.8, precompute_covariances=True):
        score = ts.EbicScore(self.data)
        score.setGamma(gamma)
        self.score = score

        self.params.set(Params.PENALTY_DISCOUNT, gamma)
        self.params.set(Params.PRECOMPUTE_COVARIANCES, precompute_covariances)
        self.SCORE = score_.EbicScore()

    def use_kim_score(self, rule_type=4, penalty_discount=1, sem_gic_rule=4):
        score = ts.KimEtAlScores(self.data)
        score.setRuleType(rule_type)
        score.setPenaltyDiscount(penalty_discount)
        self.score = score

        self.params.add(Params.SEM_GIC_RULE, sem_gic_rule)
        self.params.add(Params.PENALTY_DISCOUNT_ZS, penalty_discount)
        self.SCORE = score_.KimEtAlScores()

    def use_mixed_variable_polynomial(self, structure_prior=0, f_degree=0, discretize=False):
        score = ts.MVPScore(self.data, structure_prior, f_degree, discretize)
        self.score = score

        self.params.set(Params.structure_prior, structure_prior)
        self.params.set("fDegree", f_degree)
        self.params.set(Params.DISCRETIZE), discretize
        self.SCORE = score_.MVPBicScore()

    def use_poisson_prior(self, lambda_=2):
        score = ts.PoissonPriorScore(self.data)
        score.setLambda(lambda_)
        self.score = score

        self.params.add(Params.PRECOMPUTE_COVARIANCES)
        self.params.add(Params.POISSON_LAMBDA)
        self.SCORE = score_.PoissonPriorScore()

    def use_zhang_shen_bound(self, risk_bound=0.2):
        score = ts.ZhangShenBoundScore(self.data)
        score.setRiskBound(risk_bound)
        self.score = score

        self.params.set(Params.ZS_RISK_BOUND, risk_bound)
        self.SCORE = score_.ZhangShenBoundScore()

    def use_bdeu(self, sample_prior=10, structure_prior=0):
        score = ts.BDeuScore(self.data)
        score.setSamplePrior(sample_prior)
        score.setStructurePrior(structure_prior)
        self.score = score

        self.params.set(Params.PRIOR_EQUIVALENT_SAMPLE_SIZE, sample_prior)
        self.params.set(Params.STRUCTURE_PRIOR, structure_prior)
        self.SCORE = score_.BdeuScore()

    def use_conditional_gaussian_score(self, penalty_discount=1, discretize=True, num_categories_to_discretize=3,
                                       structure_prior=0):
        score = ts.ConditionalGaussianScore(self.data, penalty_discount, discretize)
        score.setNumCategoriesToDiscretize(num_categories_to_discretize)
        score.setStructurePrior(structure_prior)
        self.score = score

        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.STRUCTURE_PRIOR, structure_prior)
        self.params.set(Params.DISCRETIZE, discretize)
        self.params.set(Params.NUM_CATEGORIES_TO_DISCRETIZE, num_categories_to_discretize)
        self.SCORE = score_.ConditionalGaussianBicScore()

    def use_degenerate_gaussian_score(self, penalty_discount=1, structure_prior=0):
        score = ts.DegenerateGaussianScore(self.data)
        score.setPenaltyDiscount(penalty_discount)
        score.setStructurePrior(structure_prior)
        self.score = score

        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.STRUCTURE_PRIOR, structure_prior)
        self.SCORE = score_.DegenerateGaussianBicScore()

    def use_fisher_z(self, alpha=0.01):
        test = ts.IndTestFisherZ(self.data, alpha)
        self.test = test

        self.params.set(Params.ALPHA, alpha)
        self.TEST = ind_.FisherZ()

    def use_chi_square(self, alpha=0.01):
        test = ts.IndTestChiSquare(self.data, alpha)
        self.test = test

        self.params.set(Params.ALPHA, alpha)
        self.TEST = ind_.ChiSquare()

    def use_g_square(self, alpha=0.01):
        test = ts.IndTestGSquare(self.data, alpha)
        self.test = test

        self.params.set(Params.ALPHA, alpha)
        self.TEST = ind_.GSquare()

    def use_conditional_gaussian_test(self, alpha=0.01, discretize=True, num_categories_to_discretize=3):
        test = ts.IndTestConditionalGaussianLRT(self.data, alpha, discretize)
        test.setNumCategoriesToDiscretize(num_categories_to_discretize)
        self.test = test

        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.DISCRETIZE, discretize)
        self.params.set(Params.NUM_CATEGORIES_TO_DISCRETIZE, num_categories_to_discretize)
        self.TEST = ind_.ConditionalGaussianLRT()

    def use_degenerate_gaussian_test(self, alpha=0.01):
        test = ts.IndTestDegenerateGaussianLRT(self.data)
        test.setAlpha(alpha)
        self.test = test

        self.params.set(Params.ALPHA, alpha)
        self.TEST = ind_.DegenerateGaussianLRT()

    def use_probabilistic_test(self, threshold=False, cutoff=0.5, prior_ess=10):
        test = ts.IndTestProbabilistic(self.data)
        test.setThreshold(threshold)
        test.setCutoff(cutoff)
        test.setPriorEquivalentSampleSize(prior_ess)
        self.test = test

        self.params.set(Params.NO_RANDOMLY_DETERMINED_INDEPENDENCE, threshold)
        self.params.set(Params.CUTOFF_IND_TEST, cutoff)
        self.params.set(Params.PRIOR_EQUIVALENT_SAMPLE_SIZE, prior_ess)
        self.TEST = ind_.DegenerateGaussianLRT()

    def use_kci(self, alpha=0.01, approximate=True, width_multipler=1, num_bootstraps=5000, threshold=0.001,
                epsilon=0.001):
        test = ts.Kci(self.data, alpha)
        test.setApproximate(approximate)
        test.setWidthMultiplier(width_multipler)
        test.setNumBootstraps(num_bootstraps)
        test.setThreshold(threshold)
        test.setEpsilon(epsilon)
        self.test = test

        self.params.set(Params.KCI_USE_APPROMATION, approximate)
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.KERNEL_MULTIPLIER, width_multipler)
        self.params.set(Params.KCI_NUM_BOOTSTRAPS, num_bootstraps)
        self.params.set(Params.THRESHOLD_FOR_NUM_EIGENVALUES, threshold)
        self.params.set(Params.KCI_EPSILON, epsilon)
        self.TEST = ind_.Kci()

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
        alg = cpdag.FGES(self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_boss(self, depth=-1):
        self.params.set(Params.DEPTH, depth)
        alg = cpdag.BOSS(self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_sp(self):
        alg = cpdag.SP(self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_grasp(self):
        alg = cpdag.GRASP(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_gango(self):
        self.java = search.gango(self.score, self.data, self.knowledge, verbose=self.verbose)
        # alg = cpdag.BOSS(self.SCORE)
        # alg.setKnowledge(self.knowledge)
        # self.java = alg.search(self.data, self.params)

    def run_pc(self):
        alg = cpdag.PC(self.TEST)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_cpc(self):
        alg = cpdag.CPC(self.TEST)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_pcmax(self):
        alg = cpdag.PCMAX(self.TEST)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_fci(self):
        alg = pag.FCI(self.TEST)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_gfci(self):
        alg = pag.GFCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_bfci(self):
        alg = pag.BFCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_grasp_fci(self):
        alg = pag.GRASP_FCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_spfci(self):
        alg = pag.SP_FCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_ccd(self):
        if not self.knowledge.isEmpty():
            print("CCD does not use knowledge.")
            return

        alg = pag.CCD(self.TEST)
        self.java = alg.search(self.data, self.params)

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

    # Set numberResampling to 0 to turn off bootstrapping.
    def set_bootstrapping_parameters(self, numberResampling=0, percent_resample_size=100, add_original=True,
                                     with_replacement=True, resampling_ensemble=1, seed=-1):
        self.params.set(Params.NUMBER_RESAMPLING, numberResampling)
        self.params.set(Params.PERCENT_RESAMPLE_SIZE, percent_resample_size)
        self.params.set(Params.ADD_ORIGINAL_DATASET, add_original)
        self.params.set(Params.RESAMPLING_WITH_REPLACEMENT, with_replacement)
        self.params.set(Params.RESAMPLING_ENSEMBLE, resampling_ensemble)
        self.params.set(Params.SEED, seed)

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
