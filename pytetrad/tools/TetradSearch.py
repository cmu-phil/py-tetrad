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

        self.params.set(Params.SEM_GIC_RULE, sem_gic_rule)
        self.params.set(Params.PENALTY_DISCOUNT_ZS, penalty_discount)
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

        self.params.set(Params.PRECOMPUTE_COVARIANCES)
        self.params.set(Params.POISSON_LAMBDA)
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

    def run_fges(self, symmetric_first_step=False, max_degree=-1, parallelized=False,
                 faithfulness_assumed=False, meek_verbose=False):
        alg = cpdag.FGES(self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

        self.params.set(Params.SYMMETRIC_FIRST_STEP, symmetric_first_step)
        self.params.set(Params.MAX_DEGREE, max_degree)
        self.params.set(Params.PARALLELIZED, parallelized)
        self.params.set(Params.FAITHFULNESS_ASSUMED, faithfulness_assumed)
        self.params.set(Params.MEEK_VERBOSE, meek_verbose)

    def run_boss(self, num_starts = 1, depth=-1):
        self.params.set(Params.DEPTH, depth)
        alg = cpdag.BOSS(self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.NUM_STARTS, num_starts)
        self.params.set(Params.DEPTH, depth)

        self.java = alg.search(self.data, self.params)


    def run_sp(self):
        alg = cpdag.SP(self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)

    def run_grasp(self, depth=4, singular_depth=1,
                          nonsingular_depth=4, ordered_alg=True,
                          raskutti_uhler=False, use_data_order=True,
                          num_starts=1):
        alg = cpdag.GRASP(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.GRASP_DEPTH, depth)
        self.params.set(Params.GRASP_SINGULAR_DEPTH, singular_depth)
        self.params.set(Params.GRASP_NONSINGULAR_DEPTH, nonsingular_depth)
        self.params.set(Params.GRASP_ORDERED_ALG, ordered_alg)
        self.params.set(Params.GRASP_USE_RASKUTTI_UHLER, raskutti_uhler)
        self.params.set(Params.GRASP_USE_DATA_ORDER, use_data_order)
        self.params.set(Params.NUM_STARTS, num_starts)

        self.java = alg.search(self.data, self.params)

    def run_gango(self):
        self.java = search.gango(self.score, self.data, self.knowledge, verbose=self.params.getBoolean(Params.VERBOSE))

    def run_pc(self, conflict_rule=1, depth=-1, use_heuristic=True, max_path_length=-1,
               stable_fas=True):
        alg = cpdag.PC(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.CONFLICT_RULE, conflict_rule)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.USE_MAX_P_ORIENTATION_HEURISTIC, use_heuristic)
        self.params.set(Params.MAX_P_ORIENTATION_MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.STABLE_FAS, stable_fas)

        self.java = alg.search(self.data, self.params)

    def run_cpc(self, conflict_rule=1, depth=-1, use_heuristic=True, max_path_length=-1,
               stable_fas=True):
        alg = cpdag.CPC(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.CONFLICT_RUL, conflict_rule)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.USE_MAX_P_ORIENTATION_HEURISTIC, use_heuristic)
        self.params.set(Params.MAX_P_ORIENTATION_MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.STABLE_FAS, stable_fas)

        self.java = alg.search(self.data, self.params)

    def run_pcmax(self, conflict_rule=1, depth=-1, use_heuristic=True, max_path_length=-1,
               stable_fas=True):
        alg = cpdag.PCMAX(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.CONFLICT_RUL, conflict_rule)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.USE_MAX_P_ORIENTATION_HEURISTIC, use_heuristic)
        self.params.set(Params.MAX_P_ORIENTATION_MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.STABLE_FAS, stable_fas)

        self.java = alg.search(self.data, self.params)

    def run_fci(self, fas_heuristic=1, depth=-1, stable_fas=True,
                      max_path_length=-1, possible_dsep=True,
                      do_discriminating_path_rule=True,
                      complete_rule_set_used=True):
        alg = pag.FCI(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.FAS_HEURISTIC, fas_heuristic)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.POSSIBLE_DSEP_DONE, possible_dsep)
        self.params.set(Params.DO_DISCRIMINATING_PATH_RULE, do_discriminating_path_rule)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)

        self.java = alg.search(self.data, self.params)

    def run_gfci(self, depth=-1, max_degree=-1, max_path_length=-1,
                 complete_rule_set_used=True, do_discriminating_path_rule=True,
                 possible_dsep_done=True):
        alg = pag.GFCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.MAX_DEGREE, max_degree)
        self.params.set(Params.MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)
        self.params.set(Params.DO_DISCRIMINATING_PATH_RULE, do_discriminating_path_rule)
        self.params.set(Params.POSSIBLE_DSEP_DONE, possible_dsep_done)

        self.java = alg.search(self.data, self.params)

    def run_bfci(self, depth=-1, max_path_length=-1,
                 complete_rule_set_used=True, do_discriminating_path_rule=True):
        alg = pag.BFCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)
        self.params.set(Params.DO_DISCRIMINATING_PATH_RULE, do_discriminating_path_rule)

        self.java = alg.search(self.data, self.params)

    def run_grasp_fci(self, fas_heuristic=1, stable_fas=True,
                      max_path_length=-1, possible_dsep=True,
                      do_discriminating_path_rule=True,
                      complete_rule_set_used=True,
                      depth=4, singular_depth=1,
                      nonsingular_depth=4, ordered_alg=True,
                      raskutti_uhler=False, use_data_order=True,
                      num_starts=1):
        alg = pag.GRASP_FCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        # GRaSP
        self.params.set(Params.GRASP_DEPTH, depth)
        self.params.set(Params.GRASP_SINGULAR_DEPTH, singular_depth)
        self.params.set(Params.GRASP_NONSINGULAR_DEPTH, nonsingular_depth)
        self.params.set(Params.GRASP_ORDERED_ALG, ordered_alg)
        self.params.set(Params.GRASP_USE_RASKUTTI_UHLER, raskutti_uhler)
        self.params.set(Params.GRASP_USE_DATA_ORDER, use_data_order)
        self.params.set(Params.NUM_STARTS, num_starts)

        # FCI
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.FAS_HEURISTIC, fas_heuristic)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.POSSIBLE_DSEP_DONE, possible_dsep)
        self.params.set(Params.DO_DISCRIMINATING_PATH_RULE, do_discriminating_path_rule)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)

        self.java = alg.search(self.data, self.params)

    def run_sp_fci(self, max_path_length=-1, complete_rule_set_used=True,
                   do_discriminating_path_rule=True, depth=-1):
        alg = pag.SP_FCI(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.params.set(Params.MAX_PATH_LENGTH, max_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)
        self.params.set(Params.DO_DISCRIMINATING_PATH_RULE, do_discriminating_path_rule)
        self.params.set(Params.DEPTH, depth)

        self.java = alg.search(self.data, self.params)

    def run_ccd(self, depth=-1, apply_r1=True):
        if not self.knowledge.isEmpty():
            print("CCD does not use knowledge.")
            return

        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.APPLY_R1, apply_r1)

        alg = pag.CCD(self.TEST)
        self.java = alg.search(self.data, self.params)

    def run_svar_fci(self, penalty_discount=2):
        num_lags = 2
        lagged_data = ts.TimeSeriesUtils.createLagData(self.data, num_lags)
        ts_test = ts.IndTestFisherZ(lagged_data, 0.01)
        ts_score = ts.SemBicScore(lagged_data)
        ts_score.setPenaltyDiscount(penalty_discount)
        svar_fci = ts.SvarGFci(ts_test, ts_score)
        svar_fci.setKnowledge(lagged_data.getKnowledge())
        svar_fci.setVerbose(True)
        self.java = svar_fci.search()

    # Set numberResampling to 0 to turn off bootstrapping.
    def set_bootstrapping(self, numberResampling=0, percent_resample_size=100, add_original=True,
                                     with_replacement=True, resampling_ensemble=1, seed=-1):
        self.params.set(Params.NUMBER_RESAMPLING, numberResampling)
        self.params.set(Params.PERCENT_RESAMPLE_SIZE, percent_resample_size)
        self.params.set(Params.ADD_ORIGINAL_DATASET, add_original)
        self.params.set(Params.RESAMPLING_WITH_REPLACEMENT, with_replacement)
        self.params.set(Params.RESAMPLING_ENSEMBLE, resampling_ensemble)
        self.params.set(Params.SEED, seed)

    def set_verbose(self, verbose):
        self.params.set(Params.VERBOSE, verbose)

    def set_time_lag(self, time_lag=0):
        self.params.set(Params.TIME_LAG, time_lag)

    def get_data(self):
        return self.data

    def get_score(self):
        return self.score

    def get_test(self):
        return self.test

    def get_verbose(self):
        return self.params.getBoolean(Params.VERBOSE)

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
