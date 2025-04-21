# AIR Tool
#
# Copyright 2025 Carnegie Mellon University.
#
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE
# MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO
# WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER
# INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR
# MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL.
# CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT
# TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#
# Licensed under a MIT (SEI)-style license, please see license.txt or contact
# permission_at_sei.cmu.edu for full terms.
#
# [DISTRIBUTION STATEMENT A] This material has been approved for public release
# and unlimited distribution.  Please see Copyright notice for non-US Government
# use and distribution.
#
# This Software includes and/or makes use of Third-Party Software each subject to
# its own license.
#
# DM24-1686

# This class translates some select methods from TetradSearch.py in py-tetrad
# for use in R using rJava.
#
# This is a temporary class, as a much better effort at translating these
# methods is underway by another group.

TetradSearch <- setRefClass(
  "TetradSearch",

  fields = list(
    data = "data.frame",          # Input dataset
    sample_size = "numeric",      # Sample size
    data_model = "ANY",           # Data Model (Tabular data or Covariance Matrix)
    score = "ANY",                # Score object
    test = "ANY",                 # IndependenceTest object
    mc_test = "ANY",              # IndependenceTest for the Markov Checker
    mc_ind_results = "ANY",       # Markov Checker independence test results
    knowledge = "ANY",            # Background knowledge object
    graph = "ANY",                # Resulting graph
    search = "ANY",               # Search object
    params = "ANY"                # Parameters object
  ),

  methods = list(

    # Initialize the TetradSearch object
    #
    # @param data A data frame containing the dataset to be analyzed.
    # @return A TetradSearch object.
    initialize = function(data) {
      cat("Initializing TetradSearch object...\n")

      if (!is.data.frame(data)) {
        stop("Data must be a data.frame")
      }

      .self$data <- data
      .self$sample_size <- nrow(data)
      cat("Data frame dimensions:", dim(data), "\n")
      cat("Sample size set to:", .self$sample_size, "\n")

      .self$data_model <- .self$data_frame_to_tetrad_dataset(data)
      .self$data_model <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      cat("Tetrad DataSet created.\n")

      .self$params <- .jnew("edu.cmu.tetrad.util.Parameters")

      .self$knowledge <- .jnew("edu/cmu/tetrad/data/Knowledge")
      cat("Knowledge instance created.\n")
      cat("TetradSearch object initialized successfully.\n")
    },

    # Make sure the score object is initialized
    .check_score = function() {
      if (is.null(.self$score)) {
        stop("Error: The 'score' field has not been initialized yet. Please \
                 set a score before running the algorithm.")
      }
    },

    .setParam = function(key, value) {
      .jcall(.self$params, "V", "set", key, .jcast(.jnew("java/lang/Boolean", value), "java/lang/Object"))
    },

    .setParamInt = function(key, value) {
      .jcall(.self$params, "V", "set", key, .jcast(.jnew("java/lang/Integer", as.integer(value)), "java/lang/Object"))
    },

    .set_knowledge = function() {
      .jcall(.self$search, "V", "setKnowledge", .jcast(.self$knowledge, "edu.cmu.tetrad.data.Knowledge"))
    },

    # Run the search algorithm, for the typical case
    .run_search = function() {
      .self$.set_knowledge()
      .self$graph <- .jcast(.self$search$search(), "edu.cmu.tetrad.graph.Graph")
    },

    # Make sure the test object is initialized
    .check_test = function() {
      if (is.null(.self$test)) {
        stop("Error: The 'test' field has not been initialized yet. Please \
                 set a test before running the algorithm.")
      }
    },

    # Add a variable to a specific tier in the knowledge
    #
    # @param tier The tier to which the variable should be added.
    # @param var_name The name of the variable to add.
    add_to_tier = function(tier, var_name) {
      cat("Adding variable", var_name, "to tier", tier, "...\n")
      tryCatch({
        tier <- as.integer(tier)
        var_name <- as.character(var_name)
        .jcall(.self$knowledge, "V", "addToTier", tier, var_name)
        cat("Variable", var_name, "added to tier", tier, ".\n")
      }, error = function(e) {
        cat("Error adding variable to tier:", e$message, "\n")
      })
    },

    # Set the verbose flag
    #
    # @param verbose TRUE or FALSE
    set_verbose = function(verbose) {
      .self$.setParam("verbose", verbose)
    },

    # Set the score to the SEM BIC.
    #
    # @param penalty_discount The penalty discount to use in the SemBicScore calculation.
    use_sem_bic = function(penalty_discount = 2) {
      .self$.setParamDouble("penaltyDiscount", penalty_discount)
      .self$score <- .jnew("edu.cmu.tetrad.algcomparison.score.SemBicScore")
      .self$score <- .jcast(.self$score, "edu.cmu.tetrad.algcomparison.score.ScoreWrapper")
      cat("SemBicScore object created with penalty discount set.\n")
    },

    # Set the test to Fisher Z
    #
    # @param alpha The significance cutoff.
    use_fisher_z = function(alpha = 0.01, use_for_mc = FALSE) {
      .self$.setParamDouble("alpha", alpha)

      if (use_for_mc) {
        .self$mc_test <- .jnew("edu.cmu.tetrad.algcomparison.independence.FisherZ")
        .self$mc_test <- .jcast(.self$mc_test, "edu.cmu.tetrad.algcomparison.independence.IndependenceWrapper")
      } else {
        .self$test <- .jnew("edu.cmu.tetrad.algcomparison.independence.FisherZ")
        .self$test <- .jcast(.self$test, "edu.cmu.tetrad.algcomparison.independence.IndependenceWrapper")
      }

      cat("Fisher Z object created with alpha set.\n")
    },

    # Runs the PC algorithm.
    #
    # @param conflict_rule The rule used for resolving collider conflicts: 1 = prioritize existing
    #   colliders, 2 = orient bidirected edges, 3 = overwrite existing colliders.
    # @param depth The maximum number of conditioning variables per test.
    # @stable_fas TRUE is the stable FAS should be used.
    # @guarantee_cpdag TRUE is a legal CPDAG output should be guaranteed.
    # @return The estimated graph.
    run_pc = function(conflict_rule=1, depth=-1, stable_fas=TRUE, guarantee_cpdag=FALSE) {
      cat("Running PC algorithm...\n")

      .self$.setParamInt("conflictRule", conflict_rule)
      .self$.setParamInt("depth", depth)
      .self$.setParam("stableFas", stable_fas)
      .self$.setParam("guaranteePag", guarantee_cpdag)

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      pc <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag.Pc", .self$test)
      .jcall(pc, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(pc, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
      .self$graph <- graph

      cat("PC search completed.\n")
      return(.self$graph)
    },

    # Run the FGES algorithm
    #
    # @param symmetric_first_step TRUE just in case the first step in scoring should be treated symmetricaly.
    # @param max_degree The maximum degree of the graph, -1 if unlimited.
    # @param parallelized TRUE is parallelization should be used.
    # @oaram faithfulness_assumed TRUE if one-edge faithfulness should be assumed.
    # @return The estimated graph.
    run_fges = function(symmetric_first_step = FALSE, max_degree = -1, parallelized = FALSE, faithfulness_assumed = FALSE) {
      cat("Running FGES algorithm...\n")

      .self$.setParam("symmetricFirstStep", symmetric_first_step)
      .self$.setParamInt("maxDegree", max_degree)
      .self$.setParam("parallelized", parallelized)
      .self$.setParam("faithfulnessAssumed", faithfulness_assumed)

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      fges <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag.Fges", .self$score)
      .jcall(fges, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(fges, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
      .self$graph <- graph

      cat("FGES search completed.\n")
      return(.self$graph)
    },

    # --- Internal parameter helpers ---

    .setParamDouble = function(key, value) {
      .jcall(.self$params, "V", "set", key, .jcast(.jnew("java/lang/Double", as.double(value)), "java/lang/Object"))
    },

    # Run the BOSS algorithm
    #
    # @param num_starts The number of random restarts to do; the model with the best BIC score overall is returned.
    # @param use_bes TRUE if the algorithm should finish up with a call to BES (Backward Equivalence Search from
    #   the FGES algorithm) to guarantee correctness under Faithfulness.
    # @param time_lag Default 0; if > 1, a time lag model of this order is constructed.
    # @param use_data_order TRUE if the original data order should be used for the initial permutation. If
    #   num_starts > 1, random permuatations are used for subsequent restarts.
    # @param output_cpdag TRUE if a CPDAG should be output, FALSE if a DAG should be output.
    # @return The estimated graph.
    run_boss = function(num_starts = 1, use_bes = FALSE, time_lag = 0, use_data_order = TRUE, output_cpdag = TRUE) {
      cat("Running BOSS algorithm...\n")

      .self$.setParam("useBes", use_bes)
      .self$.setParamInt("numStarts", num_starts)
      .self$.setParamInt("timeLag", time_lag)
      .self$.setParam("useDataOrder", use_data_order)
      .self$.setParam("outputCpdag", output_cpdag)

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      boss <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag.Boss", .self$score)
      .jcall(boss, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(boss, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
      .self$graph <- graph

      cat("BOSS search completed.\n")
    },

    # Run the FCI algorithm
    #
    # @param depth The maximum size of any conditioning set for independence testing.
    # @param stable_fas Whether the stable version of the PC adjacency search should be used.
    # @param max_disc_path_length The maximum length of any discriminating path considered, or -1 if unlimited.
    # @param complete_rule_set_used TRUE if the tail and arrow complete (Zhang) FCI final orienation rule set
    #   should be used, FALSE if the arrow-complete rule set from Causation, Prediction and Search should be used.
    # @param guarangee_pag TRUE if a final pipeline should be run to guarantee a legal PAG estimated graph.
    # @return The estimated graph
    run_fci = function(depth = -1, stable_fas = TRUE, max_disc_path_length = -1, complete_rule_set_used = TRUE,
                       guarantee_pag = FALSE) {
      cat("Running FCI algorithm...\n")

      .self$.setParamInt("depth", depth)
      .self$.setParam("stableFas", stable_fas)
      .self$.setParamInt("maxDiscriminatingPathLength", max_disc_path_length)
      .self$.setParam("completeRuleSetUsed", complete_rule_set_used)
      .self$.setParam("guaranteePag", guarantee_pag)
      
      fci <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.pag.Fci", .self$test)
      .jcall(fci, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(fci, "Ledu/cmu/tetrad/graph/Graph;", "search", .self$data_model, .self$params)
      .self$graph <- graph

      cat("FCI search completed.\n")
    },

    # Run the BFCI algorithm
    #
    # @param depth The maximum size of any conditioning set for independence testing.
    # @param stable_fas Whether the stable version of the PC adjacency search should be used.
    # @param max_disc_path_length The maximum length of any discriminating path considered, or -1 if unlimited.
    # @param complete_rule_set_used TRUE if the tail and arrow complete (Zhang) FCI final orienation rule set
    #   should be used, FALSE if the arrow-complete rule set from Causation, Prediction and Search should be used.
    # @param guarangee_pag TRUE if a final pipeline should be run to guarantee a legal PAG estimated graph.
    # @return The estimated graph
    run_boss_fci = function(depth = -1, max_disc_path_length = -1, complete_rule_set_used = TRUE, guarantee_pag = FALSE) {
      cat("Running BOSS-FCI algorithm...\n")

      .self$.setParamInt("depth", depth)
      .self$.setParamInt("maxDiscriminatingPathLength", max_disc_path_length)
      .self$.setParam("completeRuleSetUsed", complete_rule_set_used)
      .self$.setParam("guaranteePag", guarantee_pag)

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      boss_fci <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.pag.BossFci", .self$test, .self$score)
      .jcall(boss_fci, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(boss_fci, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
      .self$graph <- graph

      cat("BOSS-FCI search completed.\n")
    },


    # Run the FCI algorithm
    #
    # @param num_starts The number initial random starts for the initial CPDAG search; the one with the best
    #   BIC score is used.
    # @param max_blocking_path_length The maximum length of any blocking path length for the testing phase.
    # @param max_disc_path_length The maximum length of any discriminating path considered, or -1 if unlimited.
    # @param depth The maximum size of any conditioning set for independence testing or -1 if unlimited.
    # @return The estimated graph
    run_fcit = function(num_starts = 1, max_blocking_path_length = 5, depth = 5, max_disc_path_length = -1) {
      cat("Running FCIT algorithm...\n")

      # BOSS parameters
      .self$.setParamInt("numStarts", num_starts)

      # FCIT parameters
      .self$.setParamInt("maxBlockingPathLength", max_blocking_path_length)
      .self$.setParamInt("depth", depth)
      .self$.setParamInt("maxDiscriminatingPathLength", max_disc_path_length)

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      fcit <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.pag.Fcit", .self$test, .self$score)
      .jcall(fcit, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(fcit, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
      .self$graph <- graph

      cat("FCIT search completed.\n")
    },

    get_java = function() {
      return(.self$graph)
    },

    # This method prints the structure of the graph estimated by the most recent algorithm call.
    print_graph = function() {
      cat("Attempting to print the graph...\n")
      if (is.null(.self$graph)) {
        cat("No graph generated yet. Please run an algorithm first.\n")
      } else {
        cat("Graph structure:\n", .self$graph$toString(), "\n")
      }
      invisible(.self$graph)
    },

    # An adjustment set for a pair of nodes <source, target> for a CPDAG is a set of nodes that blocks
    # all paths from the source to the target that cannot contribute to a calculation for the total effect
    # of the source on the target in any DAG in a CPDAG while not blocking any path from the source to the target
    # that could be causal. In typical causal graphs, multiple adjustment sets may exist for a given pair of
    # nodes. This method returns up to maxNumSets adjustment sets for the pair of nodes <source, target>
    # fitting a certain description.
    #
    # The description is as follows. We look for adjustment sets of variables that are close to either the
    # source or the target (or either) in the graph. We take all possibly causal paths from the source to the
    # target into account but only consider other paths up to a certain specified length. (This maximum length
    # can be unlimited for small graphs.)
    #
    # Within this description, we list adjustment sets in order or increasing size. Hopefully, these parameters
    # along with the size ordering can help to give guidance for the user to choose the best adjustment set for
    # their purposes when multiple adjustment sets are possible.
    #
    # @param source                  The source node whose sets will be used for adjustment.
    # @param target                  The target node whose sets will be adjusted to match the source node.
    # @param maxNumSets              The maximum number of sets to be adjusted. If this value is less than or equal to
    #                                0, all sets in the target node will be adjusted to match the source node.
    # @param maxDistanceFromEndpoint The maximum distance from the endpoint of the trek to consider for adjustment.
    # @param nearWhichEndpoint       The endpoint(s) to consider for adjustment; 1 = near the source, 2 = near the
    #                                target, 3 = near either.
    # @param maxPathLength           The maximum length of the path to consider for backdoor paths. If a value of -1 is
    #                                given, all paths will be considered.
    # @return A list of adjustment sets for the pair of nodes &lt;source, target&gt;. Return an smpty
    # list if source == target or there is no amenable path from source to target.
    get_adjustment_sets = function(graph, source, target, max_num_sets = 10, max_distance_from_point = 5,
                                   near_which_endpoint = 1, max_path_length = 20) {
      cat("Getting adjustment sets for:", source, "->", target, "\n")

      # Look up Node objects by name
      source_node <- .jcall(graph, "Ledu/cmu/tetrad/graph/Node;", "getNode", source)
      target_node <- .jcall(graph, "Ledu/cmu/tetrad/graph/Node;", "getNode", target)

      if (is.jnull(source_node)) stop(paste("Source node", source, "not found in the graph."))
      if (is.jnull(target_node)) stop(paste("Target node", target, "not found in the graph."))

      # Get Paths object from Graph
      paths <- .jcall(graph, "Ledu/cmu/tetrad/graph/Paths;", "paths")

      # Java List<Set<Node>>
      sets_list <- .jcall(paths,
                          "Ljava/util/List;",
                          "adjustmentSets",
                          source_node,
                          target_node,
                          as.integer(max_num_sets),
                          as.integer(max_distance_from_point),
                          as.integer(near_which_endpoint),
                          as.integer(max_path_length))


      size <- .jcall(sets_list, "I", "size")
      cat("Number of adjustment sets:", size, "\n")

      # Convert Java List<Set<Node>> to R list of character vectors
      size <- .jcall(sets_list, "I", "size")
      result <- vector("list", size)

      for (i in seq_len(size)) {
        jset <- .jcall(sets_list, "Ljava/lang/Object;", "get", as.integer(i - 1))
        jarray <- .jcall(jset, "[Ljava/lang/Object;", "toArray")
        result[[i]] <- sapply(jarray, function(n) .jcall(n, "S", "getName"))
      }

      return(result)
    },

    print_adjustment_sets = function(adjustment_sets) {
      if (length(adjustment_sets) == 0) {
        cat("No adjustment sets found.\n")
        return()
      }

      for (i in seq_along(adjustment_sets)) {
        set <- adjustment_sets[[i]]
        cat(sprintf("Adjustment set %d: ", i))
        if (length(set) == 0) {
          cat("(empty set)\n")
        } else {
          cat(paste(set, collapse = ", "), "\n")
        }
      }
    },

    # Performs a Markov check on a graph with respect to the supplied dataset and returns statistics
    # showing performance on that check.
    #
    # @param graph The graph to perform the Markov check on. This may be a DAG, CPDAG, MAG or PAG.
    # @param percent_resample Tests are done using random subsamples of the data per test, if this is
    #   less than 1, or all of the data, if it is equal to 1.
    # @param condition_set_type The type of conditioning set to use for the Markov check, one of:
    #   GLOBAL_MARKOV, LOCAL_MARKOV, PARENTS_AND_NEIGHBORS, MARKOV_BLANKET, RECURSIVE_MSEP, NONCOLLIDERS_ONLY,
    #   ORDERED_LOCAL_MARKOV, or ORDERED_LOCAL_MARKOV_MAG
    # @param find_smallest_subset Whether to find the smallest subset for a given set that yields independence.
    # @param parallelized TRUE if conditional independencies should be checked in parallel.
    # @effective_sample_size The effective sample size to use for calculations, or -1 if the actual sample size.
    # @return Marov checker statistics as a named list.
    markov_check = function(graph, percent_resample = 1, condition_set_type = "ORDERED_LOCAL_MARKOV",
                            find_smallest_subset = FALSE, parallelized = TRUE) {
      cat("Running Markov check...\n")

      if (is.null(.self$mc_test)) {
        stop("A test for the Markov Checker has not been set. Please call a `use_*` method with `use_for_mc = TRUE`.")
      }

      condition_set_type_ <- .jfield("edu.cmu.tetrad.search.ConditioningSetType",
                                    name = condition_set_type,
                                    sig = "Ledu/cmu/tetrad/search/ConditioningSetType;")

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      test_ <- .jcall(.self$mc_test, "Ledu/cmu/tetrad/search/IndependenceTest;",
                     "getTest", dataModel, .self$params)

      mc <- .jnew("edu.cmu.tetrad.search.MarkovCheck", graph, test_, condition_set_type_)

      # Configure it
      .jcall(mc, "V", "setPercentResample", as.double(percent_resample))
      .jcall(mc, "V", "setFindSmallestSubset", find_smallest_subset)
      .jcall(mc, "V", "setParallelized", parallelized)

      # Generate results
      .jcall(mc, "V", "generateAllResults")
      .self$mc_ind_results <- .jcall(mc, "Ljava/util/List;", "getResults", TRUE)

      # # Set sample size if specified
      # if (sample_size != -1) {
      #   .jcall(mc, "V", "setSampleSize", as.integer(sample_size))
      # }

      # Extract statistics
      ad_ind <- .jcall(mc, "D", "getAndersonDarlingP", TRUE)
      ad_dep <- .jcall(mc, "D", "getAndersonDarlingP", FALSE)
      ks_ind <- .jcall(mc, "D", "getKsPValue", TRUE)
      ks_dep <- .jcall(mc, "D", "getKsPValue", FALSE)
      bin_indep <- .jcall(mc, "D", "getBinomialPValue", TRUE)
      bin_dep <- .jcall(mc, "D", "getBinomialPValue", FALSE)
      frac_dep_ind <- .jcall(mc, "D", "getFractionDependent", TRUE)
      frac_dep_dep <- .jcall(mc, "D", "getFractionDependent", FALSE)
      num_tests_ind <- .jcall(mc, "I", "getNumTests", TRUE)
      num_tests_dep <- .jcall(mc, "I", "getNumTests", FALSE)

      # Return as a named list
      return(list(
        ad_ind = ad_ind,
        ad_dep = ad_dep,
        ks_ind = ks_ind,
        ks_dep = ks_dep,
        bin_indep = bin_indep,
        bin_dep = bin_dep,
        frac_dep_ind = frac_dep_ind,
        frac_dep_dep = frac_dep_dep,
        num_tests_ind = num_tests_ind,
        num_tests_dep = num_tests_dep,
        mc = mc
      ))
    },

    # Converts the given R data frame to a (possibly mixed) Tetrad DataSet.
    #
    # @param df The R data frame to translate. Continuous columns should be of type 'numeric' and the
    #   discrete columns of type 'integer'.
    data_frame_to_tetrad_dataset = function(df) {
      stopifnot(require(rJava))

      nrows <- nrow(df)
      ncols <- ncol(df)

      # Create Java ArrayList<Node>
      var_list <- .jnew("java/util/ArrayList")

      # Prepare empty double[][] and int[][] (as Java arrays)
      cont_data <- vector("list", ncols)
      disc_data <- vector("list", ncols)

      for (j in seq_len(ncols)) {
        name <- colnames(df)[j]
        col <- df[[j]]

        if (is.numeric(col)) {
          variable <- .jnew("edu/cmu/tetrad/data/ContinuousVariable", name)
          node <- .jcast(variable, "edu/cmu/tetrad/graph/Node")
          .jcall(var_list, "Z", "add", .jcast(node, "java/lang/Object"))
          cont_data[[j]] <- .jarray(as.numeric(col), dispatch = TRUE)
          disc_data[[j]] <- .jnull("[I")  # null int[] for discrete
        } else if (is.integer(col) || is.factor(col)) {
          num_categories <- length(unique(na.omit(col)))
          variable <- .jnew("edu/cmu/tetrad/data/DiscreteVariable", name, as.integer(num_categories))
          node <- .jcast(variable, "edu/cmu/tetrad/graph/Node")
          .jcall(var_list, "Z", "add", .jcast(node, "java/lang/Object"))
          cont_data[[j]] <- .jnull("[D")  # null double[] for continuous
          disc_data[[j]] <- .jarray(as.integer(col), dispatch = TRUE)
        } else {
          stop(paste("Unsupported column type:", name))
        }
      }

      # Convert R lists of arrays to Java double[][] and int[][]
      j_cont_data <- .jarray(cont_data, dispatch = TRUE)
      j_disc_data <- .jarray(disc_data, dispatch = TRUE)

      # Call static Java helper method
      ds <- .jcall("edu.cmu.tetrad.util.DataSetHelper",
                   "Ledu/cmu/tetrad/data/DataSet;",
                   "fromR",
                   .jcast(var_list, "java.util.List"),
                   as.integer(nrows),
                   .jcast(j_cont_data, "[[D"),
                   .jcast(j_disc_data, "[[I"))

      return(ds)
    }
  )
)
