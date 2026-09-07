## This assumes that you have already started the JVM using JPype. You may
## start the JVM only once per session. Your code should start with the following
## lines:
#
import jpype
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

## Some functions wrapping various classes in Tetrad. Feel free to just steal
## the relevant code for your own projects, or 'pip install' this Github directory
## and call these functions. will add more named parameters to help one see which 
## methods for the the searches can be controlled.

from edu.cmu.tetrad.util import Params, Parameters
import edu.cmu.tetrad.algcomparison.simulation as sim
import edu.cmu.tetrad.algcomparison.graph as graph

# Simuolates a continuous dataset with the given arguments and returns the dataset as a pandas datafram
def simulateLinearFisher(num_meas = 20, num_lat = 0, avg_deg = 4, samp_size = 200, coef_low = 0, coef_high = 1,
                         var_low = 1, var_high = 3, rand_cols=False):
    # Set the parameters for the simulation
    params = Parameters()

    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.NUM_MEASURES, num_meas)
    params.set(Params.AVG_DEGREE, avg_deg)
    params.set(Params.NUM_LATENTS, num_lat)
    params.set(Params.RANDOMIZE_COLUMNS, rand_cols) # Prevents some algorithsm from taking advantage of true causal order
    params.set(Params.COEF_LOW, coef_low)
    params.set(Params.COEF_HIGH, coef_high)
    params.set(Params.VAR_LOW, var_low)
    params.set(Params.VAR_HIGH, var_high)
    params.set(Params.INTERVAL_BETWEEN_SHOCKS, 30)
    params.set(Params.INTERVAL_BETWEEN_RECORDINGS, 30)
    params.set(Params.VERBOSE, False)
    params.set(Params.NUM_RUNS, 1)
    # params.set(Params.SEED, 29483)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.LinearFisherModel(graph.RandomForward())
    sim_.createData(params, True)

    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    return D, G

def simulateSemSimulation(num_meas = 20, num_lat = 0, avg_deg = 4, samp_size = 200, coef_low = 0, coef_high = 1,
                         var_low = 1, var_high = 3, rand_cols=False):
    # Set the parameters for the simulation
    params = Parameters()

    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.NUM_MEASURES, num_meas)
    params.set(Params.AVG_DEGREE, avg_deg)
    params.set(Params.NUM_LATENTS, num_lat)
    params.set(Params.RANDOMIZE_COLUMNS, rand_cols) # Prevents some algorithsm from taking advantage of true causal order
    params.set(Params.COEF_LOW, coef_low)
    params.set(Params.COEF_HIGH, coef_high)
    params.set(Params.VAR_LOW, var_low)
    params.set(Params.VAR_HIGH, var_high)
    params.set(Params.VERBOSE, False)
    params.set(Params.NUM_RUNS, 1)
    # params.set(Params.SEED, 29483)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.SemSimulation(graph.RandomForward())
    sim_.createData(params, True)

    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    return D, G

def simulateGeneralNoise(num_meas = 20, num_lat = 0, avg_deg = 4, samp_size = 200,
                          rand_cols=False):
    # Set the parameters for the simulation
    params = Parameters()

    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.NUM_MEASURES, num_meas)
    params.set(Params.AVG_DEGREE, avg_deg)
    params.set(Params.NUM_LATENTS, num_lat)
    params.set(Params.RANDOMIZE_COLUMNS, rand_cols) # Prevents some algorithsm from taking advantage of true causal order
    # params.set(Params.COEF_LOW, coef_low)
    # params.set(Params.COEF_HIGH, coef_high)
    # params.set(Params.VAR_LOW, var_low)
    # params.set(Params.VAR_HIGH, var_high)
    params.set(Params.VERBOSE, False)
    params.set(Params.NUM_RUNS, 1)
    # params.set(Params.SEED, 29483)

    # params.set(Params.NOISE_EXPRESSION)
    # params.set(Params.HIDDEN_DIMENSIONS)
    # params.set(Params.INPUT_SCALE)
    # params.set(Params.NUM_RUNS)
    # params.set(Params.PROB_REMOVE_COLUMN)
    # params.set(Params.DIFFERENT_GRAPHS)
    # params.set(Params.RANDOMIZE_COLUMNS)
    # params.set(Params.SAMPLE_SIZE)
    # params.set(Params.SAVE_LATENT_VARS)
    # params.set(Params.STANDARDIZE)
    # params.add(Params.SEED)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.GeneralNoiseSimulation(graph.RandomForward())
    sim_.createData(params, True)

    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    return D, G

# Simulates a discrete dataset with the given arguments and returns the dataset as a pandas dataframe
def simulateDiscrete(num_meas = 20, num_lat = 0, avg_deg = 4, min_cat=3, max_cat=3, samp_size=1000):
    # Set the parameters for the simulation
    params = Parameters()

    # Params for graph
    params.set(Params.NUM_MEASURES, num_meas)
    params.set(Params.NUM_LATENTS, num_lat)
    params.set(Params.AVG_DEGREE, avg_deg)

    # Params for Bayes PM
    params.set(Params.MIN_CATEGORIES, min_cat)
    params.set(Params.MAX_CATEGORIES, max_cat)

    # Params for simuulation
    params.set(Params.RANDOMIZE_COLUMNS, True) # Prevents some algorithms from taking advantage of causal order
    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.SAVE_LATENT_VARS, False)
    # params.set(Params.SEED, 29483)

    params.set(Params.NUM_RUNS, 1)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.BayesNetSimulation(graph.RandomForward())
    sim_.createData(params, True)
    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    return D, G

# Simulates a discrete dataset with the given arguments and returns the dataset as a pandas dataframe
def simulateDiscreteFromGraph(tetrad_graph, min_cat=3, max_cat=3, samp_size=1000):
    # Set the parameters for the simulation
    params = Parameters()

    # Params for Bayes PM
    params.set(Params.MIN_CATEGORIES, min_cat)
    params.set(Params.MAX_CATEGORIES, max_cat)

    # Params for simuulation
    params.set(Params.RANDOMIZE_COLUMNS, True) # Prevents some algorithms from taking advantage of causal order
    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.SAVE_LATENT_VARS, False)
    # params.set(Params.SEED, 29483

    params.set(Params.NUM_RUNS, 1)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.BayesNetSimulation(graph.SingleGraph(tetrad_graph))
    sim_.createData(params, True)
    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    return D, G

# Simulates data with the anatomy of a designed physical experiment (archetype: the NASA
# Airfoil Self-Noise dataset). Variables come in three tiers: grid-valued design factors
# (F1, ...), near-deterministic derived intermediates (D1, ...), and interaction-heavy
# responses (R1, ...). See the Javadoc of
# edu.cmu.tetrad.algcomparison.simulation.DesignedExperimentSimulation for details.
#
# Defaults below match the Tetrad parameter defaults.
#
# Returns (D, G, K, sim_): the dataset, the true (pre-selection) DAG, the design-implied
# knowledge, and the simulation object itself. K is a Tetrad Knowledge object with role
# tiers -- factors (F) before derived (D) before responses (R), and CONFIG, if emitted, in
# a leading tier of its own (its fixed-effects reading) -- which an analyst of such data
# would legitimately have; it says nothing about the random structure within a role. Pass
# it to TetradSearch.set_knowledge(K). The simulation object gives access to
# sim_.getConfigurationStarts(0), the starting row of each configuration block when
# sort_by_configuration is True.
#
# Note: when selection > 0, the observed data contains input-input dependence NOT in the
# true graph; that is by design. When emit_config_column is True, a discrete CONFIG
# bookkeeping column is appended; exclude it from search.
def simulateDesignedExperiment(num_factors=4, num_derived=1, num_responses=1,
                               min_levels=4, max_levels=12, coupling=0.5,
                               derived_noise=0.05, interaction=0.5, response_noise=0.4,
                               selection=0.0, sort_by_configuration=False,
                               emit_config_column=False, samp_size=1000,
                               rand_cols=False, seed=None):
    # Set the parameters for the simulation
    params = Parameters()

    params.set(Params.DE_NUM_FACTORS, num_factors)
    params.set(Params.DE_NUM_DERIVED, num_derived)
    params.set(Params.DE_NUM_RESPONSES, num_responses)
    params.set(Params.DE_MIN_LEVELS, min_levels)
    params.set(Params.DE_MAX_LEVELS, max_levels)
    params.set(Params.DE_COUPLING, coupling)
    params.set(Params.DE_DERIVED_NOISE, derived_noise)
    params.set(Params.DE_INTERACTION, interaction)
    params.set(Params.DE_RESPONSE_NOISE, response_noise)
    params.set(Params.DE_SELECTION, selection)
    params.set(Params.DE_SORT_BY_CONFIGURATION, sort_by_configuration)
    params.set(Params.DE_EMIT_CONFIG_COLUMN, emit_config_column)

    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.RANDOMIZE_COLUMNS, rand_cols)  # Note: the tiered column order (F, D, R) is informative
    params.set(Params.VERBOSE, False)
    params.set(Params.NUM_RUNS, 1)
    if seed is not None:
        params.set(Params.SEED, seed)

    # Do the simulation and grab the dataset and generative graph. The RandomGraph
    # argument is ignored; the tiered structure is generated internally.
    sim_ = sim.DesignedExperimentSimulation(graph.RandomForward())
    sim_.createData(params, True)

    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)
    K = sim_.getKnowledge(0)

    return D, G, K, sim_

# Simulates data with the anatomy of an observational study (archetype: the Algerian
# Forest Fire dataset). Variables have roles: observed/hidden context variables (exogenous
# drivers), system variables (the causal system proper), near-deterministic index chains,
# and outcomes (optionally discrete via logits). Options, all off by default, include
# serial dependence (max_lag > 0; the true graph is then a lag graph, with the
# contemporaneous summary graph available from the simulation object), panel structure
# (num_subjects > 1), latent confounding (num_hidden_context > 0), ordinalization,
# censoring at detection limits, and MCAR/MAR/MNAR missingness. See the Javadoc of
# edu.cmu.tetrad.algcomparison.simulation.ObservationalStudySimulation for details.
#
# Defaults below match the Tetrad parameter defaults. NOTE: prop_missing defaults to 0.1
# in Tetrad but only takes effect when missing_mechanism is not "none".
#
# Discrete variables: prop_context_discrete is a per-variable coin flip over the context
# variables (exogenous); discrete_outcome makes the outcomes discrete (terminal);
# prop_system_discrete makes a fixed count round(prop * num_system) of the SYSTEM variables
# genuinely discrete, so a discrete cause can sit inside the graph with both parents and
# children (the case where CG and DG scores differ). prop_ordinalized, by contrast, records
# continuous system variables as categories -- coarsening, not a discrete cause.
#
# Panel emission (num_subjects > 1): by default the subjects are concatenated into one
# dataset with the structure undeclared, as panel data usually arrive. With
# emit_subject_column=True a discrete bookkeeping column SUBJECT is appended (not in the
# true graph; use it for grouping, centering, or as a tier-0 fixed-effects variable, and
# otherwise exclude it from search). With emit_subjects_as_data_sets=True each subject is
# emitted as its own dataset sharing the true graph -- the form consumed by IMaGES-style
# pooling (TetradSearch.add_data_set / set_pool_data_sets) -- and D is then a Python LIST
# of datasets, one per subject.
#
# Returns (D, G, K, sim_): the dataset (or list of per-subject datasets, see above), the
# true graph (a lag graph when max_lag > 0; with latent nodes when num_hidden_context > 0,
# so FCI-style evaluation works), the design-implied knowledge, and the simulation object
# itself. K is a Tetrad Knowledge object with role tiers -- context (C) before system (S)
# before indices (I) before outcomes (Y), and SUBJECT, if emitted, in a leading tier of its
# own (its fixed-effects reading) -- which an analyst of such data would legitimately have;
# it says nothing about the random structure within a role. Pass it to
# TetradSearch.set_knowledge(K). In serial mode it is knowledge over the contemporaneous
# variables; lag tiers come from the lag-data machinery. The simulation object gives access
# to sim_.getContemporaneousGraph(i), sim_.getSubjectStarts(i), and sim_.getKnowledge(i).
def simulateObservationalStudy(num_context=2, num_hidden_context=0, num_system=6,
                               num_indices=2, num_outcomes=1, avg_system_degree=2.0,
                               prop_context_discrete=0.5, prop_system_discrete=0.0,
                               num_categories=3,
                               discrete_outcome=False, prop_ordinalized=0.0,
                               max_lag=0, ar_coef=0.7, index_memory_low=0.2,
                               index_memory_high=0.9, prop_cross_lag=0.15,
                               num_subjects=1, emit_subject_column=False,
                               emit_subjects_as_data_sets=False,
                               index_noise=0.05, nonlinearity=0.3,
                               interaction=0.2, edge_density=1.0,
                               missing_mechanism="none", prop_missing=0.1,
                               prop_censored=0.0, censor_quantile=0.9,
                               samp_size=1000, seed=None):
    if missing_mechanism not in ("none", "mcar", "mar", "mnar"):
        raise ValueError("missing_mechanism must be one of: none, mcar, mar, mnar")

    # Set the parameters for the simulation
    params = Parameters()

    params.set(Params.OS_GRAPH_NUM_CONTEXT, num_context)
    params.set(Params.OS_GRAPH_NUM_HIDDEN_CONTEXT, num_hidden_context)
    params.set(Params.OS_GRAPH_NUM_SYSTEM, num_system)
    params.set(Params.OS_GRAPH_NUM_INDICES, num_indices)
    params.set(Params.OS_GRAPH_NUM_OUTCOMES, num_outcomes)
    params.set(Params.OS_GRAPH_AVG_SYSTEM_DEGREE, avg_system_degree)
    params.set(Params.OS_TYPE_PROP_CONTEXT_DISCRETE, prop_context_discrete)
    params.set(Params.OS_TYPE_PROP_SYSTEM_DISCRETE, prop_system_discrete)
    params.set(Params.OS_TYPE_NUM_CATEGORIES, num_categories)
    params.set(Params.OS_TYPE_DISCRETE_OUTCOME, discrete_outcome)
    params.set(Params.OS_DEGRADE_ORDINALIZE_PROP, prop_ordinalized)
    params.set(Params.OS_SERIAL_MAX_LAG, max_lag)
    params.set(Params.OS_SERIAL_AR_COEF, ar_coef)
    params.set(Params.OS_SERIAL_INDEX_MEMORY_LOW, index_memory_low)
    params.set(Params.OS_SERIAL_INDEX_MEMORY_HIGH, index_memory_high)
    params.set(Params.OS_SERIAL_PROP_CROSS_LAG, prop_cross_lag)
    params.set(Params.OS_PANEL_NUM_SUBJECTS, num_subjects)
    params.set(Params.OS_PANEL_EMIT_SUBJECT_COLUMN, emit_subject_column)
    params.set(Params.OS_PANEL_EMIT_SUBJECTS_AS_DATA_SETS, emit_subjects_as_data_sets)
    params.set(Params.OS_FORM_INDEX_NOISE, index_noise)
    params.set(Params.OS_FORM_NONLINEARITY, nonlinearity)
    params.set(Params.OS_FORM_INTERACTION, interaction)
    params.set(Params.OS_GRAPH_EDGE_DENSITY, edge_density)
    params.set(Params.OS_DEGRADE_MISSING_MECHANISM, missing_mechanism)
    params.set(Params.OS_DEGRADE_MISSING_PROP, prop_missing)
    params.set(Params.OS_DEGRADE_CENSOR_PROP, prop_censored)
    params.set(Params.OS_DEGRADE_CENSOR_QUANTILE, censor_quantile)

    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.VERBOSE, False)
    params.set(Params.NUM_RUNS, 1)
    if seed is not None:
        params.set(Params.SEED, seed)

    # Do the simulation and grab the dataset and generative graph. The RandomGraph
    # argument is ignored; the role structure is generated internally.
    sim_ = sim.ObservationalStudySimulation(graph.RandomForward())
    sim_.createData(params, True)

    if emit_subjects_as_data_sets and num_subjects > 1:
        D = [sim_.getDataModel(i) for i in range(sim_.getNumDataModels())]
    else:
        D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)
    K = sim_.getKnowledge(0)

    return D, G, K, sim_

# Simuolates a mixed continuous/discrete dataset using the Lee-Hastic method with the given arguments
# and returns the dataset as a pandas dataframe.
def simulateLeeHastie(num_meas = 20, num_lat = 0, avg_deg = 4, min_cat=3, max_cat=3, perc_disc=50, samp_size=1000):

    # Set the parameters for the simulation
    params = Parameters()

    params.set(Params.NUM_MEASURES, num_meas)
    params.set(Params.NUM_LATENTS, num_lat)
    params.set(Params.AVG_DEGREE, avg_deg)

    params.set(Params.MIN_CATEGORIES, min_cat)
    params.set(Params.MAX_CATEGORIES, max_cat)
    params.set(Params.PERCENT_DISCRETE, perc_disc)
    params.set(Params.DIFFERENT_GRAPHS, False)

    params.set(Params.RANDOMIZE_COLUMNS, True) # Preents some algorithsm from taking advantage of causal order
    params.set(Params.SAMPLE_SIZE, samp_size)
    params.set(Params.SAVE_LATENT_VARS, False)
    # params.set(Params.SEED, 29493L)

    params.set(Params.NUM_RUNS, 1)

    # Do the simulation and grab the dataset and generative graph
    sim_ = sim.LeeHastieSimulation(graph.RandomForward())
    sim_.createData(params, True)
    D = sim_.getDataModel(0)
    G = sim_.getTrueGraph(0)

    return D, G

    # D_ = tr.tetrad_to_pandas(D)
    # G_ = tr.tetrad_graph_to_causal_learn(G)
    #
    # return D_, G_
