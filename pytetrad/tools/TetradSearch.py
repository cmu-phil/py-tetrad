## Provides a simple wrapper for many of the Tetrad searches that can be used
## either from Python or from R. The inputs are all pandas data frames
## and the outputs are endpoint-matrix-formatted graphs, also data frames. (In a
## future version, we may allow the outputs to be given other formats.)

import importlib.resources as importlib_resources

import jpype.imports

# print('cwd = ', os.getcwd())

# jar_path = importlib_resources.files('pytetrad').joinpath('resources', 'tetrad-current.jar')
# jar_path = str(jar_path)
# if not jpype.isJVMStarted():
#     try:
#         jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
#     except OSError:
#         print("can't load jvm")
#         pass

import pytetrad.tools.translate as tr
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as gr
import edu.cmu.tetrad.graph.GraphSaveLoadUtils as gp
import java.lang as lang
import java.util as util
import edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag as cpdag
import edu.cmu.tetrad.algcomparison.algorithm.oracle.pag as pag
import edu.cmu.tetrad.algcomparison.algorithm.continuous.dag as dag
import edu.cmu.tetrad.algcomparison.algorithm.cluster as cluster
import edu.cmu.tetrad.algcomparison.score as score_
import edu.cmu.tetrad.algcomparison.independence as ind_
import edu.cmu.tetrad.search.utils as search_utils
import edu.cmu.tetrad.algcomparison.algorithm.other as alg_other

import java.io as io

from edu.cmu.tetrad.util import Params, Parameters


class TetradSearch:
    """
    Represents a Tetrad-based search class for structure learning and related statistical scoring and testing 
    functionalities.

    This class initializes and manages various scoring and independence test mechanisms based on configurations
    passed via methods. It adapts Tetrad functionalities while offering Pythonic interaction. The usage entails
    interacting with the attributes and methods to configure the scoring or testing criteria for causal discovery
    and structure learning.

    :ivar data: Data used for analysis, converted to Tetrad-compatible format.
    :type data: object
    :ivar score: The current scoring function in use.
    :type score: object or None
    :ivar TEST: The current independence test in use.
    :type TEST: object or None
    :ivar java: Accessor or object for Java-based dependencies, if any.
    :type java: object or None
    :ivar knowledge: Object to manage and store prior knowledge constraints.
    :type knowledge: Knowledge
    :ivar params: Parameters object for controlling scoring or testing properties.
    :type params: Parameters
    :ivar bootstrap_graphs: Stores results of any bootstrapped graph estimation run.
    :type bootstrap_graphs: object or None
    """
    def __init__(self, df):
        self.data = tr.pandas_data_to_tetrad(df)
        self.SCORE = None
        self.TEST = None
        self.MC_TEST = None
        self.java = None
        self.knowledge = td.Knowledge()
        self.mc_knowledge = None
        self.params = Parameters()
        self.bootstrap_graphs = None

    def __str__(self):
        display = [self.SCORE, self.TEST, self.knowledge, self.java]
        return "\n\n".join([str(item) for item in display])

    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_sem_bic(self, penalty_discount=2, structurePrior=0, sem_bic_rule=1, singularity_lambda=0.0):
        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.SEM_BIC_STRUCTURE_PRIOR, structurePrior)
        self.params.set(Params.SEM_BIC_RULE, sem_bic_rule)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.SCORE = score_.SemBicScore()

    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_ebic(self, gamma=0.8, precompute_covariances=True, singularity_lambda=0.0):
        self.params.set(Params.EBIC_GAMMA, gamma)
        self.params.set(Params.PRECOMPUTE_COVARIANCES, precompute_covariances)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.SCORE = score_.EbicScore()

    def use_gic_score(self, penalty_discount=1, sem_gic_rule=4):
        self.params.set(Params.SEM_GIC_RULE, sem_gic_rule)
        self.params.set(Params.PENALTY_DISCOUNT_ZS, penalty_discount)
        self.SCORE = score_.KimEtAlScores()

    def use_mixed_variable_polynomial(self, structure_prior=0, f_degree=0, discretize=False):
        self.params.set(Params.STRUCTURE_PRIOR, structure_prior)
        self.params.set("fDegree", f_degree)
        self.params.set(Params.DISCRETIZE), discretize
        self.SCORE = score_.MVPBicScore()

    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_poisson_prior_score(self, poisson_lambda=2, precompute_covariances=True, singularity_lambda=0.0):
        self.params.set(Params.PRECOMPUTE_COVARIANCES, precompute_covariances)
        self.params.set(Params.POISSON_LAMBDA, poisson_lambda)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.SCORE = score_.PoissonPriorScore()

    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_zhang_shen_bound(self, risk_bound=0.2, singularity_lambda=0.0):
        self.params.set(Params.ZS_RISK_BOUND, risk_bound)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.SCORE = score_.ZhangShenBoundScore()

    def use_bdeu(self, sample_prior=10, structure_prior=0):
        self.params.set(Params.PRIOR_EQUIVALENT_SAMPLE_SIZE, sample_prior)
        self.params.set(Params.STRUCTURE_PRIOR, structure_prior)
        self.SCORE = score_.BdeuScore()

    def use_conditional_gaussian_score(self, penalty_discount=1, discretize=True, num_categories_to_discretize=3,
                                       structure_prior=0):
        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.STRUCTURE_PRIOR, structure_prior)
        self.params.set(Params.DISCRETIZE, discretize)
        self.params.set(Params.NUM_CATEGORIES_TO_DISCRETIZE, num_categories_to_discretize)
        self.SCORE = score_.ConditionalGaussianBicScore()

    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_degenerate_gaussian_score(self, penalty_discount=1, structure_prior=0, singularity_lambda=0.0):
        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.STRUCTURE_PRIOR, structure_prior)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.SCORE = score_.DegenerateGaussianBicScore()

    # Uses covariance as a sufficient statistic
    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_basis_function_bic(self, truncation_limit=3, penalty_discount=2, singularity_lambda=0.0,
                               do_one_equation_only=False):
        self.params.set(Params.TRUNCATION_LIMIT, truncation_limit)
        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.params.set(Params.DO_ONE_EQUATION_ONLY, do_one_equation_only)
        self.SCORE = score_.BasisFunctionBicScore()

    # Full sample.
    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_basis_function_bic_fs(self, truncation_limit=3, penalty_discount=2, singularity_lambda=0.0,
                                  do_one_equation_only=False):
        self.params.set(Params.TRUNCATION_LIMIT, truncation_limit)
        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.params.set(Params.DO_ONE_EQUATION_ONLY, do_one_equation_only)
        self.SCORE = score_.BasisFunctionBicScoreTabular()

    # Uses covariance as a sufficient statistic.
    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_basis_function_lrt(self, truncation_limit=3, alpha=0.01, use_for_mc=False, singularity_lambda=0.0,
                               do_one_equation_only=False):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.TRUNCATION_LIMIT, truncation_limit)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.params.set(Params.DO_ONE_EQUATION_ONLY, do_one_equation_only)

        if use_for_mc:
            self.MC_TEST = ind_.BasisFunctionLrt()
        else:
            self.TEST = ind_.BasisFunctionLrt()

    # Full sample
    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_basis_function_lrt_fs(self, truncation_limit=3, alpha=0.01, use_for_mc=False, singularity_lambda=0.0,
                                  do_one_equation_only=False):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.TRUNCATION_LIMIT, truncation_limit)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)
        self.params.set(Params.DO_ONE_EQUATION_ONLY, do_one_equation_only)

        if use_for_mc:
            self.MC_TEST = ind_.BasisFunctionLrtFullSample()
        else:
            self.TEST = ind_.BasisFunctionLrtFullSample()

    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_fisher_z(self, alpha=0.01, use_for_mc=False, singularity_lambda=0.0):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)

        if use_for_mc:
            self.MC_TEST = ind_.FisherZ()
        else:
            self.TEST = ind_.FisherZ()


    # This conflicts--to use a particular test like this, you should do the whole thing in JPype.
    # # The supplied test should implement edu.cmu.tetrad.algcomparison.independence.IndependenceWrapper in Tetrad.
    # def use_test(self, test, use_for_mc=False):
    #     if use_for_mc:
    #         self.MC_TEST = test
    #     else:
    #         self.TEST = test

    # cell table type is 1 = AD Tree, 2 = Count Sample. (Optimization.)
    def use_chi_square(self, min_count=1, alpha=0.01, cell_table_type=1, use_for_mc=False):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.MIN_COUNT_PER_CELL, min_count)
        self.params.set(Params.CELL_TABLE_TYPE, cell_table_type)

        if use_for_mc:
            self.MC_TEST = ind_.ChiSquare()
        else:
            self.TEST = ind_.ChiSquare()

    # cell table type is 1 = AD Tree, 2 = Count Sample. (Optimization)
    def use_g_square(self, min_count=1, alpha=0.01, cell_table_type=1, use_for_mc=False):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.MIN_COUNT_PER_CELL, min_count)
        self.params.set(Params.CELL_TABLE_TYPE, cell_table_type)

        if use_for_mc:
            self.MC_TEST = ind_.GSquare()
        else:
            self.TEST = ind_.GSquare()

    def use_conditional_gaussian_test(self, alpha=0.01, discretize=True,
                                      num_categories_to_discretize=3, use_for_mc=False):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.DISCRETIZE, discretize)
        self.params.set(Params.NUM_CATEGORIES_TO_DISCRETIZE, num_categories_to_discretize)
        self.TEST = ind_.ConditionalGaussianLrt()

        if use_for_mc:
            self.MC_TEST = ind_.ConditionalGaussianLrt()
        else:
            self.TEST = ind_.ConditionalGaussianLrt()

    # singularity_lambda: >= 0 Add lambda to matrix diagonals, < 0 Use pseudoinverse
    def use_degenerate_gaussian_test(self, alpha=0.01, use_for_mc=False, singularity_lambda=0.0):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.SINGULARITY_LAMBDA, singularity_lambda)

        if use_for_mc:
            self.MC_TEST = ind_.DegenerateGaussianLrt()
        else:
            self.TEST = ind_.DegenerateGaussianLrt()

    def use_probabilistic_test(self, threshold=False, cutoff=0.5, prior_ess=10, use_for_mc=False):
        self.params.set(Params.NO_RANDOMLY_DETERMINED_INDEPENDENCE, threshold)
        self.params.set(Params.CUTOFF_IND_TEST, cutoff)
        self.params.set(Params.PRIOR_EQUIVALENT_SAMPLE_SIZE, prior_ess)

        if use_for_mc:
            self.MC_TEST = ind_.ProbabilisticTest()
        else:
            self.TEST = ind_.ProbabilisticTest()

    def use_kci(self, alpha=0.01, approximate=True, scaling_factor=1, num_bootstraps=5000, threshold=1e-3,
                epsilon=1e-3, kernel_type=1, polyd=5, polyc=1, use_for_mc=False):
        self.params.set(Params.KCI_USE_APPROXIMATION, approximate)
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.SCALING_FACTOR, scaling_factor)
        self.params.set(Params.KCI_NUM_BOOTSTRAPS, num_bootstraps)
        self.params.set(Params.THRESHOLD_FOR_NUM_EIGENVALUES, threshold)
        self.params.set(Params.KCI_EPSILON, epsilon)
        self.params.set(Params.KERNEL_TYPE, kernel_type)
        self.params.set(Params.POLYNOMIAL_DEGREE, polyd)
        self.params.set(Params.POLYNOMIAL_CONSTANT, polyc)

        if use_for_mc:
            self.MC_TEST = ind_.Kci()
        else:
            self.TEST = ind_.Kci()

    def use_cci(self, alpha=0.01, scaling_factor=2, num_basis_functions=3, basis_type=4,
                basis_scale=0.0, use_for_mc=False):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.SCALING_FACTOR, scaling_factor)
        self.params.set(Params.NUM_BASIS_FUNCTIONS, num_basis_functions)
        self.params.set(Params.BASIS_TYPE, basis_type)
        self.params.set(Params.BASIS_SCALE, basis_scale)

        if use_for_mc:
            self.MC_TEST = ind_.CciTest()
        else:
            self.TEST = ind_.CciTest()

    def add_to_tier(self, tier, var_name):
        self.knowledge.addToTier(lang.Integer(tier), lang.String(var_name))

    def set_tier_forbidden_within(self, tier, forbiddenWithin=True):
        self.knowledge.setTierForbiddenWithin(lang.Integer(tier), forbiddenWithin)

    def set_forbidden(self, var_name_1, var_name_2):
        self.knowledge.setForbidden(lang.String(var_name_1), lang.String(var_name_2))

    def set_required(self, var_name_1, var_name_2):
        self.knowledge.setRequired(lang.String(var_name_1), lang.String(var_name_2))

    def set_knowledge(self, knowledge):
        self.knowledge = knowledge

    def clear_knowledge(self):
        self.knowledge.clear()

    def load_knowledge(self, path, use_for_mc=False):
        """
        Loads knowledge from the specified file and sets it in the appropriate knowledge object (either
        the main knowledge or the Monte Carlo (MC) knowledge) depending on the use_for_mc flag.

        Note that knowledge for the algorithm is a different type of knowledge from what you use for the Markov checker.
        Here is the doc for Markov checker knowledge: "Sets the knowledge object for the Markov checker. The knowledge
        object should contain the tier knowledge for the Markov checker. The last tier contains the possible X and Y for
        X _||_ Y | Z1,...,Zn, and the previous tiers contain the possible Z1,...,Zn for X _||_ Y | Z1,...,Zn.
        Additional forbidden or required edges are ignored.
    
        :param path: The file path to the knowledge file that contains prior constraints.
        :type path: str
        :param use_for_mc: If True, loads the knowledge into the Monte Carlo (MC) knowledge object;
                           otherwise, loads it into the main knowledge object.
        :type use_for_mc: bool
        :return: None
        """
        if use_for_mc:
            know_file = io.File(path)
            know_delim = td.DelimiterType.WHITESPACE
            self.mc_knowledge = td.SimpleDataLoader.loadKnowledge(know_file, know_delim, "#")
        else:
            know_file = io.File(path)
            know_delim = td.DelimiterType.WHITESPACE
            self.knowledge = td.SimpleDataLoader.loadKnowledge(know_file, know_delim, "#")

    def check_knowledge(self):
        X = [str(x) for x in self.knowledge.getVariables()]
        Y = [str(y) for y in self.data.getVariableNames()]
        return [x for x in X if x not in Y]

    def print_knowledge(self):
        print(self.knowledge)

    def run_fges(self, symmetric_first_step=False, max_degree=-1, parallelized=False,
                 faithfulness_assumed=False):
        alg = cpdag.Fges(self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.SYMMETRIC_FIRST_STEP, symmetric_first_step)
        self.params.set(Params.MAX_DEGREE, max_degree)
        self.params.set(Params.PARALLELIZED, parallelized)
        self.params.set(Params.FAITHFULNESS_ASSUMED, faithfulness_assumed)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_fges_mb(self, targets="", max_degree=-1, trimming_style=3,
                    number_of_expansions=2, faithfulness_assumed=False):
        alg = cpdag.FgesMb(self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.params.set(Params.TARGETS, targets)
        self.params.set(Params.FAITHFULNESS_ASSUMED, faithfulness_assumed)
        self.params.set(Params.MAX_DEGREE, max_degree)
        self.params.set(Params.TRIMMING_STYLE, trimming_style)
        self.params.set(Params.NUMBER_OF_EXPANSIONS, number_of_expansions)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_boss(self, num_starts=1, use_bes=False, time_lag=0, use_data_order=True,
                 output_cpdag=True):
        self.params.set(Params.USE_BES, use_bes)
        self.params.set(Params.NUM_STARTS, num_starts)
        self.params.set(Params.TIME_LAG, time_lag)
        self.params.set(Params.USE_DATA_ORDER, use_data_order)
        self.params.set(Params.OUTPUT_CPDAG, output_cpdag)
        alg = cpdag.Boss(self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_restricted_boss(self, targets="", use_bes=False, num_starts=1,
                            allow_internal_randomness=True):
        self.params.set(Params.TARGETS, targets)
        self.params.set(Params.USE_BES, use_bes)
        self.params.set(Params.NUM_STARTS, num_starts)
        self.params.set(Params.ALLOW_INTERNAL_RANDOMNESS, allow_internal_randomness)

        alg = cpdag.RestrictedBoss(self.SCORE)
        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    # Algorithm. This is the algorithm to use to calculate bootstrapped CPDAGs.
    # Current options are PC Stable, FGES, BOSS, or Restricted BOSS. For large
    # datasets, we recommend Restricted BOSS, which calculates variables with
    # marginal effect on one of the targets and then runs BOSS over this restricted
    # set.
    # Results Output Path. A default is “cstar-out”, which will place result-files
    # in a subdirectory of the current directory named path = “cstar-out”.[n], where
    # n is the first index for which no such directory exists. If a directory already
    # exists at the path, then any information available in path directory will be
    # used to generate results in the path-.[n] directory.
    # Number of Subsamples. CStaR finds CPDAGs over subsampled data of size n / 2; this
    # specifies how many subsamples to use.
    # Minimum effect size. This allows a shorter table to be produced. It this is set
    # to a value m > 0, then only records with PI > m will be displayed.
    # Target Names. A list of names of variables (comma or space separated) can be
    # given that are considered possible effects. These will be excluded from the list
    # of possible causes, which will be all other variables in the dataset.
    # Top Bracket. The CStaR algorithm tries to find possible causes that regularly sort
    # into the top set of variables by minimum IDA effect. This gives the number q of
    # variables to include in the top bracket, where 1 <= q <= # possible causes.
    # Parallelized. Yes, if the search should be parallelized, no if not. Default no.
    def run_cstar(self, targets="", file_out_path="cstar-out", selection_min_effect=0.0,
                  num_subsamples=50, top_bracket=10, parallelized=False, cpdag_algorithm=4,
                  remove_effect_nodes=True, sample_style=1):
        self.params.set(Params.SELECTION_MIN_EFFECT, selection_min_effect)
        self.params.set(Params.NUM_SUBSAMPLES, num_subsamples)
        self.params.set(Params.TARGETS, targets)
        self.params.set(Params.TOP_BRACKET, top_bracket)
        self.params.set(Params.PARALLELIZED, parallelized)
        self.params.set(Params.CSTAR_CPDAG_ALGORITHM, cpdag_algorithm)
        self.params.set(Params.FILE_OUT_PATH, file_out_path)
        self.params.set(Params.REMOVE_EFFECT_NODES, remove_effect_nodes)
        self.params.set(Params.SAMPLE_STYLE, sample_style)

        alg = cpdag.Cstar(self.TEST, self.SCORE)
        self.java = alg.search(self.data, self.params)

    def run_sp(self):
        alg = cpdag.Sp(self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)
        alg.setKnowledge(self.knowledge)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_grasp(self, covered_depth=4, singular_depth=1,
                  nonsingular_depth=1, ordered_alg=False,
                  raskutti_uhler=False, use_data_order=True,
                  num_starts=1):
        self.params.set(Params.GRASP_DEPTH, covered_depth)
        self.params.set(Params.GRASP_SINGULAR_DEPTH, singular_depth)
        self.params.set(Params.GRASP_NONSINGULAR_DEPTH, nonsingular_depth)
        self.params.set(Params.GRASP_ORDERED_ALG, ordered_alg)
        self.params.set(Params.GRASP_USE_RASKUTTI_UHLER, raskutti_uhler)
        self.params.set(Params.USE_DATA_ORDER, use_data_order)
        self.params.set(Params.NUM_STARTS, num_starts)

        alg = cpdag.Grasp(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_pc(self, conflict_rule=1, depth=-1, stable_fas=True, guarantee_cpdag=False):
        self.params.set(Params.CONFLICT_RULE, conflict_rule)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.GUARANTEE_CPDAG, guarantee_cpdag)

        alg = cpdag.Pc(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_pc_max(self, conflict_rule=1, depth=-1, stable_fas=True, guarantee_cpdag=True):
        self.params.set(Params.CONFLICT_RULE, conflict_rule)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.GUARANTEE_CPDAG, guarantee_cpdag)

        alg = cpdag.PcMax(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_cpc(self, conflict_rule=1, depth=-1, stable_fas=True, guarantee_cpdag=False):
        self.params.set(Params.CONFLICT_RULE, conflict_rule)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.GUARANTEE_CPDAG, guarantee_cpdag)

        alg = cpdag.Cpc(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_pcmax(self, conflict_rule=1, depth=-1, use_heuristic=True, max_disc_path_length=-1,
                  stable_fas=True):
        self.params.set(Params.CONFLICT_RULE, conflict_rule)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.USE_MAX_P_ORIENTATION_HEURISTIC, use_heuristic)
        self.params.set(Params.MAX_P_ORIENTATION_MAX_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.STABLE_FAS, stable_fas)

        alg = cpdag.PcMax(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_fci(self, depth=-1, stable_fas=True, max_disc_path_length=-1, complete_rule_set_used=True,
                guarantee_pag=False):
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        alg = pag.Fci(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_fci_max(self, depth=-1, stable_fas=True, max_disc_path_length=-1, complete_rule_set_used=True,
                    guarantee_pag=False):
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        alg = pag.FciMax(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_rfci(self, depth=-1, stable_fas=True, max_disc_path_length=-1, complete_rule_set_used=True, ):
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)

        alg = pag.Rfci(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_cfci(self, depth=-1, max_disc_path_length=-1, complete_rule_set_used=True):
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)

        alg = pag.Cfci(self.TEST)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    # This is GFCI with the possible d-sep step.
    def run_gfci(self, depth=-1, max_degree=-1, max_disc_path_length=-1, complete_rule_set_used=True,
                 guarantee_pag=False):
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.MAX_DEGREE, max_degree)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used),
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        alg = pag.Gfci(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    # This is GFCI without the possible d-sep step
    def run_fges_fci(self, depth=-1, max_degree=-1, max_disc_path_length=-1, complete_rule_set_used=True,
                 guarantee_pag=False):
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.MAX_DEGREE, max_degree)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used),
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        alg = pag.Gfci(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_boss_fci(self, depth=-1, max_disc_path_length=-1, complete_rule_set_used=True,
                 guarantee_pag=False):
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used),
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        alg = pag.BossFci(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_boss_pod(self, num_starts=1, use_bes=False, time_lag=0, use_data_order=True,
                     output_cpdag=True, complete_rule_set_used=True):
        self.params.set(Params.USE_BES, use_bes)
        self.params.set(Params.NUM_STARTS, num_starts)
        self.params.set(Params.TIME_LAG, time_lag)
        self.params.set(Params.USE_DATA_ORDER, use_data_order)
        self.params.set(Params.OUTPUT_CPDAG, output_cpdag)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used),

        alg = pag.BossPod(self.SCORE)

        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_fcit(self, num_starts=1, max_blocking_path_length=5, depth=5, max_disc_path_length=5,
                    guarantee_pag=True):
        # BOSS
        self.params.set(Params.NUM_STARTS, num_starts)

        # FCIT
        self.params.set(Params.MAX_BLOCKING_PATH_LENGTH, max_blocking_path_length)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        alg = pag.Fcit(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_grasp_fci(self, depth=-1, stable_fas=True,
                      max_disc_path_length=-1,
                      complete_rule_set_used=True,
                      covered_depth=4, singular_depth=1,
                      nonsingular_depth=1, ordered_alg=False,
                      raskutti_uhler=False, use_data_order=True,
                      num_starts=1, guarantee_pag=False):
        # GRaSP
        self.params.set(Params.GRASP_DEPTH, covered_depth)
        self.params.set(Params.GRASP_SINGULAR_DEPTH, singular_depth)
        self.params.set(Params.GRASP_NONSINGULAR_DEPTH, nonsingular_depth)
        self.params.set(Params.GRASP_ORDERED_ALG, ordered_alg)
        self.params.set(Params.GRASP_USE_RASKUTTI_UHLER, raskutti_uhler)
        self.params.set(Params.USE_DATA_ORDER, use_data_order)
        self.params.set(Params.NUM_STARTS, num_starts)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        # FCI
        self.params.set(Params.DEPTH, depth)
        # self.params.set(Params.FAS_HEURISTIC, fas_heuristic)
        self.params.set(Params.STABLE_FAS, stable_fas)
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)

        alg = pag.GraspFci(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_spfci(self, max_disc_path_length=-1, complete_rule_set_used=True, depth=-1,
                  guarantee_pag=False):
        self.params.set(Params.MAX_DISCRIMINATING_PATH_LENGTH, max_disc_path_length)
        self.params.set(Params.COMPLETE_RULE_SET_USED, complete_rule_set_used)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.GUARANTEE_PAG, guarantee_pag)

        alg = pag.SpFci(self.TEST, self.SCORE)
        alg.setKnowledge(self.knowledge)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_ica_lingam(self, ica_a=1.1, ica_max_iter=5000, ica_tolerance=1e-8, threshold_b=0.1):
        self.params.set(Params.FAST_ICA_A, ica_a)
        self.params.set(Params.FAST_ICA_MAX_ITER, ica_max_iter)
        self.params.set(Params.FAST_ICA_TOLERANCE, ica_tolerance)
        self.params.set(Params.THRESHOLD_B, threshold_b)

        alg = dag.IcaLingam()
        self.java = alg.search(self.data, self.params)
        self.bhat = alg.getBHat()
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    ## Returns the b-hat from the ICA-LiNGAM algorithm as a numpy array.
    def get_bhat(self):
        return tr.tetrad_matrix_to_pandas(self.bhat, self.data.getVariableNames())

    def run_ica_lingd(self, ica_a=1.1, ica_max_iter=5000, ica_tolerance=1e-8, threshold_b=0.1, threshold_w=0.1):
        self.params.set(Params.FAST_ICA_A, ica_a)
        self.params.set(Params.FAST_ICA_MAX_ITER, ica_max_iter)
        self.params.set(Params.FAST_ICA_TOLERANCE, ica_tolerance)
        self.params.set(Params.THRESHOLD_B, threshold_b)
        self.params.set(Params.THRESHOLD_W, threshold_w)

        alg = dag.IcaLingD()
        self.java = alg.search(self.data, self.params)
        self.unstable_bhats = alg.getUnstableBHats()
        self.stable_bhats = alg.getStableBHats()
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_fask(self, alpha=0.05, depth=-1, fask_delta=-0.3, left_right_rule=1, skew_edge_threshold=0.3):
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.FASK_DELTA, fask_delta)
        self.params.set(Params.FASK_LEFT_RIGHT_RULE, left_right_rule)
        self.params.set(Params.SKEW_EDGE_THRESHOLD, skew_edge_threshold)

        alg = dag.Fask(self.SCORE)
        alg.setKnowledge(self.knowledge)
        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_fofc(self, alpha=0.001, penalty_discount=2.0, tetrad_test=1,
                 include_structure_model=True, precompute_covariances=True, include_all_nodes=False):
        """
        Executes the FOFC (Fast Orientation of Factor Causal) clustering algorithm with the specified
        parameters and data provided to the class instance. This method sets up necessary configurations,
        initializes FOFC, and runs the clustering process based on user inputs.

        :param alpha: The significance level used in the FOFC algorithm. Determines the threshold for
            statistical tests during clustering.
        :type alpha: float
        :param penalty_discount: Regulates the penalty applied during the clustering process for
            handling score-based evaluations.
        :type penalty_discount: float
        :param tetrad_test: Specifies the tetrad test to be applied in the algorithm. This governs
            statistical test variations in identifying tetrad relations. 1 = CCA, 2 = Bollen-Ting,
            3 = Wishart
        :type tetrad_test: int
        :param include_structure_model: Determines whether the structural model should be considered
            during the clustering process. This applies Mimbuild.
        :type include_structure_model: bool
        :param precompute_covariances: If True, precomputes covariance matrices to optimize the algorithm's
            performance during execution.
        :type precompute_covariances: bool
        :param include_all_nodes: If True, all variables are included in the returned graph; if
            false, only clustered variables. (Default = false)
        :type include_all_nodes: boolean
        :rtype: A graph indicating clusters
        """

        # Set algorithm parameters in the Params object
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.TETRAD_TEST_FOFC, tetrad_test)
        self.params.set(Params.INCLUDE_STRUCTURE_MODEL, include_structure_model)
        self.params.set(Params.INCLUDE_ALL_NODES, include_all_nodes)
        self.params.set(Params.PRECOMPUTE_COVARIANCES, precompute_covariances)

        # Initialize the FOFC clustering algorithm
        alg = cluster.Fofc()

        # Run the search algorithm using the data and specified parameters
        self.java = alg.search(self.data, self.params)

    def run_bpc(self, alpha=0.001, penalty_discount=2.0, check_type=3,
                 include_structure_model=True, precompute_covariances=True):
        """
        Executes the BPC (Bayesian Profile Clustering) algorithm using the specified
        parameters. The function configures algorithm parameters, initializes the BPC
        clustering algorithm, and performs the search process using the provided data
        and configured options.

        :param alpha: Significance level parameter used in the algorithm.
        :type alpha: float
        :param penalty_discount: Discounting factor for penalization in the algorithm.
        :type penalty_discount: float
        :param check_type: 1 = Significance, 2 = Clique (default), 3 = None
        :type check_type: int
        :param include_structure_model: Specifies whether to include structural model
            considerations during computation.
        :type include_structure_model: bool
        :param precompute_covariances: Specifies whether to precompute covariance
            matrices for efficiency in calculations.
        :type precompute_covariances: bool
        :return: Returns a graph indicating clusters
        :rtype: object
        """
        # Set algorithm parameters in the Params object
        self.params.set(Params.ALPHA, alpha)
        self.params.set(Params.PENALTY_DISCOUNT, penalty_discount)
        self.params.set(Params.INCLUDE_STRUCTURE_MODEL, include_structure_model)
        self.params.set(Params.CHECK_TYPE, check_type)
        self.params.set(Params.PRECOMPUTE_COVARIANCES, precompute_covariances)

        # Initialize the BPC clustering algorithm
        alg = cluster.Bpc()

        # Run the search algorithm using the data and specified parameters
        self.java = alg.search(self.data, self.params)

    def run_factor_analysis(self, fa_threshold=0.001, num_factors=2.0, use_varimax=True,
                convergence_threshold=0.001):
        """
        Run factor analysis using specified parameters and a predefined dataset.

        This method initializes and configures the factor analysis algorithm with the
        provided parameter values and executes it using the given data and parameter
        configuration. Factor analysis is used to identify potential underlying
        factors that may explain the observed relationships among variables.

        :param fa_threshold: Threshold for factor analysis convergence criterion.
        :param num_factors: The number of factors to extract during analysis.
        :param use_varimax: Flag indicating whether to apply Varimax rotation to the
            extracted factors.
        :param convergence_threshold: Minimum threshold for algorithm convergence.
        :return: None
        """
        # Set algorithm parameters in the Params object
        self.params.set("fa_threshold", fa_threshold)
        self.params.set("numFactors", num_factors)
        self.params.set("useVarimax", use_varimax)
        self.params.set("convergenceThreshold", convergence_threshold)

        # Initialize the BPC clustering algorithm
        alg = alg_other.FactorAnalysis()

        # Run the search algorithm using the data and specified parameters
        self.java = alg.search(self.data, self.params)

    ## Returns the unstable b-hats from the ICA-LiNG-D algorithm as a list of numpy arrays.
    def get_unstable_bhats(self):
        list_of_matrices = []

        for i in range(self.unstable_bhats.size()):
            array = self.unstable_bhats.get(i)
            m = tr.tetrad_matrix_to_pandas(array, self.data.getVariableNames())
            list_of_matrices.append(m)

        return list_of_matrices

    ## Returns the stable b-hats from the ICA-LiNG-D algorithm as a list of numpy arrays.
    def get_stable_bhats(self):
        list_of_matrices = []

        for i in range(self.stable_bhats.size()):
            array = self.stable_bhats.get(i)
            m = tr.tetrad_matrix_to_pandas(array, self.data.getVariableNames())
            list_of_matrices.append(m)

        return list_of_matrices

    def run_ccd(self, depth=-1, apply_r1=True):
        if not self.knowledge.isEmpty():
            print("CCD does not use knowledge.")
            return

        self.params.set(Params.DEPTH, depth)
        self.params.set(Params.APPLY_R1, apply_r1)

        alg = pag.Ccd(self.TEST)
        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_svar_fci(self, penalty_discount=2):
        num_lags = 2
        lagged_data = ts.TimeSeriesUtils.createLagData(self.data, num_lags)
        ts_test = ts.IndTestFisherZ(lagged_data, 0.01)
        ts_score = ts.SemBicScore(lagged_data)
        ts_score.setPenaltyDiscount(penalty_discount)
        svar_fci = ts.SvarFci(ts_test)
        svar_fci.setKnowledge(lagged_data.getKnowledge())
        self.java = svar_fci.search()
        # self.bootstrap_graphs = svar_fci.getBootstrapGraphs()

    def run_direct_lingam(self):
        alg = dag.DirectLingam(self.SCORE)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_dagma(self, dagma_lambda=0.05, w_threshold=0.1, cpdag=True):
        alg = dag.Dagma()

        self.params.set(Params.LAMBDA1, dagma_lambda)
        self.params.set(Params.W_THRESHOLD, w_threshold)
        self.params.set(Params.CPDAG, cpdag)

        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_pc_lingam(self):
        alg = dag.PcLingam()
        self.java = alg.search(self.data, self.params)
        self.bootstrap_graphs = alg.getBootstrapGraphs()

    def run_svar_gfci(self, penalty_discount=2):
        num_lags = 2
        lagged_data = ts.utils.TsUtils.createLagData(self.data, num_lags)
        ts_test = ts.test.IndTestFisherZ(lagged_data, 0.01)
        ts_score = ts.score.SemBicScore(lagged_data, True)
        ts_score.setPenaltyDiscount(penalty_discount)
        svar_fci = ts.SvarGfci(ts_test, ts_score)
        svar_fci.setKnowledge(lagged_data.getKnowledge())
        svar_fci.setVerbose(True)
        self.java = svar_fci.search()
        # self.bootstrap_graphs = svar_fci.getBootstrapGraphs()

    def run_gango(self, score, data):
        fges_graph = TetradSearch.run_fges(score)
        datasets = util.ArrayList()
        datasets.add(data)
        rskew = ts.Lofs2(fges_graph, datasets)
        rskew.setKnowledge(self.knowledge)
        rskew.setRule(ts.Lofs2.Rule.RSkew)
        gango_graph = rskew.orient()
        return gango_graph

    # Set numberResampling to 0 to turn off bootstrapping.
    def set_bootstrapping(self, numberResampling=0, percent_resample_size=100, add_original=True,
                          with_replacement=True, resampling_ensemble=1, seed=-1):
        self.params.set(Params.NUMBER_RESAMPLING, numberResampling)
        self.params.set(Params.PERCENT_RESAMPLE_SIZE, percent_resample_size)
        self.params.set(Params.ADD_ORIGINAL_DATASET, add_original)
        self.params.set(Params.RESAMPLING_WITH_REPLACEMENT, with_replacement)
        self.params.set(Params.RESAMPLING_ENSEMBLE, resampling_ensemble)
        self.params.set(Params.SEED, seed)

    def set_data(self, data):
        self.data = tr.pandas_data_to_tetrad(data)

    def set_verbose(self, verbose):
        self.params.set(Params.VERBOSE, verbose)

    def set_time_lag(self, time_lag=0):
        self.params.set(Params.TIME_LAG, time_lag)

    def get_data(self):
        return self.data

    def get_verbose(self):
        return self.params.getBoolean(Params.VERBOSE)

    def get_knowledge(self):
        return self.knowledge

    def get_java(self):
        return self.java

    def get_string(self, java=None):
        if (java == None):
            return lang.String @ self.java.toString()
        else:
            lang.String @ java.toString()

    def get_dag_string(self, java=None):
        if (java == None):
            dag = gr.GraphTransforms.dagFromCpdag(self.java)
            return lang.String @ dag.toString()
        else:
            dag = gr.GraphTransforms.dagFromCpdag(java)
            return lang.String @ dag.toString()

    def get_dag_java(self, java=None):
        if (java == None):
            dag = gr.GraphTransforms.dagFromCpdag(self.java)
            return dag
        else:
            dag = gr.GraphTransforms.dagFromCpdag(java)
            return dag

    def get_causal_learn(self, java=None):
        if (java == None):
            return tr.tetrad_graph_to_causal_learn(self.java)
        else:
            tr.tetrad_graph_to_causal_learn(java)

    def get_graph_to_matrix(self, java=None, nullEpt=0, circleEpt=1, arrowEpt=2, tailEpt=3):
        if (java == None):
            return tr.graph_to_matrix(self.java, nullEpt, circleEpt, arrowEpt, tailEpt)
        else:
            tr.graph_to_matrix(java)

    def get_dot(self, java=None):
        if (java == None):
            return str(gp.graphToDot(self.java))
        else:
            return str(gp.graphToDot(java))

    def get_xml(self, java=None):
        if (java == None):
            return str(gp.graphToXml(self.java))
        else:
            return str(gp.graphToXml(self.java))

    def get_lavaan(self, java=None):
        if (java == None):
            return gp.graphToLavaan(self.java)
        else:
            return gp.graphToLavaan(java)

    def bootstrap_graph(self, index):
        i = lang.Integer(index).intValue()
        if i < 0 or i > len(self.bootstrap_graphs):
            raise ValueError("index out of bounds (0-indexed)")
        return self.bootstrap_graphs[i]

    def bootstrap_dot(self, index):
        i = lang.Integer(index).intValue()
        if i < 0 or i > len(self.bootstrap_graphs):
            raise ValueError("index out of bounds")
        java = self.bootstrap_graphs[i]
        return str(gp.graphToDot(java))

    def is_legal_pag(self, graph):
        return search_utils.GraphSearchUtils.isLegalPag(graph).isLegalPag()

    def is_legal_pag_reason(self, graph):
        print(search_utils.GraphSearchUtils.isLegalPag(graph).getReason())

    def all_subsets_independence_facts(self, graph):
        msep = (ts.MarkovCheck(graph, ts.test.IndTestFisherZ(self.data, 0.01), ts.ConditioningSetType.LOCAL_MARKOV)
                .getAllSubsetsIndependenceFacts().getMsep())

        facts = []

        for i in range(0, msep.size()):
            fact = msep.get(i)
            x = fact.getX().toString()
            y = fact.getY().toString()
            zlist = util.ArrayList(fact.getZ())

            _fact = []
            _fact.append(x)
            _fact.append(y)

            for j in range(0, zlist.size()):
                _fact.append(zlist.get(j).toString())

            facts.append(_fact)

        return facts

    def all_subsets_dependence_facts(self, graph):
        mconn = ts.MarkovCheck.getAllSubsetsIndependenceFacts(graph, self.TEST,
                                                              ts.ConditioningSetType.LOCAL_MARKOV).getMconn()

        facts = []

        for i in range(0, mconn.size()):
            fact = mconn.get(i)
            x = fact.getX().toString()
            y = fact.getY().toString()
            zlist = util.ArrayList(fact.getZ())

            _fact = []
            _fact.append(x)
            _fact.append(y)

            for j in range(0, zlist.size()):
                _fact.append(zlist.get(j).toString())

            facts.append(_fact)

        return facts

    def markov_check(self, graph, fraction_resample=1, condition_set_type=ts.ConditioningSetType.ORDERED_LOCAL_MARKOV,
                     removeExtraneous=False, parallelized=True, effective_sample_size=-1):
        if self.MC_TEST == None:
            raise Exception("A test for the Markov Checker has not been set. Please call as use_{test name} method setting the parmaeter 'use_for_mc' to True")

        mc = ts.MarkovCheck(graph, self.MC_TEST.getTest(self.data, self.params), condition_set_type)
        mc.setFractionResample(fraction_resample)
        mc.setFindSmallestSubset(removeExtraneous)
        mc.setParallelized(parallelized)

        if self.mc_knowledge is not None:
            mc.setKnowledge(self.mc_knowledge)

        mc.generateAllResults()

        self.mc_ind_results = mc.getResults(True)

        # Set sample size if specified
        if effective_sample_size != -1:
            mc.setEffectiveSampleSize(effective_sample_size)

        ad_ind = mc.getAndersonDarlingP(True)
        ad_dep = mc.getAndersonDarlingP(False)
        ks_ind = mc.getKsPValue(True)
        ks_dep = mc.getKsPValue(False)
        bin_indep = mc.getBinomialPValue(True)
        bin_dep = mc.getBinomialPValue(False)
        frac_dep_ind = mc.getFractionDependent(True)
        frac_dep_dep = mc.getFractionDependent(False)
        num_tests_ind = mc.getNumTests(True)
        num_tests_dep = mc.getNumTests(False)
        return (ad_ind, ad_dep, ks_ind, ks_dep, bin_indep, bin_dep, frac_dep_ind, frac_dep_dep, num_tests_ind,
                num_tests_dep, mc)

    def get_mc_ind_pvalues(self):
        pvalues = []
        results = self.mc_ind_results

        for i in range(results.size()):
            r = results.get(i)
            pvalues.append(r.getPValue())

        return pvalues

    # Returns a (tetrad-format) List of Sets of Nodes. Each set of nodes in the list is an adjustment set
    # for the source/target pair.f
    # near_which_endpoint: The endpoint(s) to consider for adjustment; 1 = near the source, 2 = near the target, 3 = near either.
    def get_adjustment_sets(self, graph, source, target, max_num_sets=10, max_distance_from_point=5,
                            near_which_endpoint=1, max_path_length=20):
        return graph.paths().adjustmentSets(source, target, max_num_sets, max_distance_from_point,
                                             near_which_endpoint, max_path_length)


def mimbuild(clustering, measure_names, latent_names, cov, full_graph=False):
    mb = ts.Mimbuild()
    graph = mb.search(clustering, measure_names, latent_names, cov)

    if full_graph:
        return mb.getFullGraph()
    else:
        return graph