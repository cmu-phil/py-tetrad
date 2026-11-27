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
    params = "ANY",               # Parameters object
    topk_graphs = "list",         # Graphs of the models kept by the last run_boss_topk, best first
    topk_scores = "numeric",      # Their scores
    topk_orders = "list",         # Their variable orders, as character vectors
    topk_num_runs = "numeric",    # How many runs that search made; NA if the jar does not say
    topk_stopped = "logical",     # Whether its cap on runs cut it short; NA if the jar does not say
    topk_result = "ANY"           # The graph that run returned
  ),

  methods = list(

    # Initialize the TetradSearch object
    #
    # @param data A data frame containing the dataset to be analyzed.
    # @param int_as_cont TRUE, the default, to take a column of type 'integer' as continuous; FALSE to take it
    #   as discrete. See data_frame_to_tetrad_dataset.
    # @return A TetradSearch object.
    initialize = function(data, int_as_cont = TRUE) {
      cat("Initializing TetradSearch object...\n")

      if (!is.data.frame(data)) {
        stop("Data must be a data.frame")
      }

      .self$data <- data
      .self$sample_size <- nrow(data)
      cat("Data frame dimensions:", dim(data), "\n")
      cat("Sample size set to:", .self$sample_size, "\n")

      .self$data_model <- .self$data_frame_to_tetrad_dataset(data, int_as_cont = int_as_cont)
      .self$data_model <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      cat("Tetrad DataSet created.\n")

      .self$params <- .jnew("edu.cmu.tetrad.util.Parameters")

      .self$knowledge <- .jnew("edu/cmu/tetrad/data/Knowledge")
      cat("Knowledge instance created.\n")
      cat("TetradSearch object initialized successfully.\n")
    },

    # Make sure the score object is initialized
    .check_score = function() {
      if (is.null(.self$score) || is(.self$score, "uninitializedField")) {
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
      if (is.null(.self$test) || is(.self$test, "uninitializedField")) {
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

    # --- Scores and tests for discrete and mixed data ---
    #
    # The arguments and their defaults are those of the methods of the same names in py-tetrad's
    # TetradSearch, so that the same call gives the same search in R and in Python.
    #
    # Which to use:
    #   every column discrete:        use_bdeu;  use_chi_square or use_g_square
    #   discrete and continuous both: use_conditional_gaussian_score or use_degenerate_gaussian_score;
    #                                 use_conditional_gaussian_test or use_degenerate_gaussian_test
    # A factor, character or logical column of the data frame is discrete; see data_frame_to_tetrad_dataset.

    # Sets the score to the named class of edu.cmu.tetrad.algcomparison.score.
    .use_score = function(class_name) {
      .self$score <- .jcast(.jnew(paste0("edu.cmu.tetrad.algcomparison.score.", class_name)),
                            "edu.cmu.tetrad.algcomparison.score.ScoreWrapper")
      cat(class_name, "object created.\n")
    },

    # Sets the test, or the Markov checker's test if use_for_mc is TRUE, to the named class of
    # edu.cmu.tetrad.algcomparison.independence.
    .use_test = function(class_name, use_for_mc = FALSE) {
      wrapper <- .jcast(.jnew(paste0("edu.cmu.tetrad.algcomparison.independence.", class_name)),
                        "edu.cmu.tetrad.algcomparison.independence.IndependenceWrapper")

      if (use_for_mc) {
        .self$mc_test <- wrapper
      } else {
        .self$test <- wrapper
      }

      cat(class_name, "object created", if (use_for_mc) "for the Markov checker.\n" else "for searching.\n")
    },

    # Set the score to BDeu, for data in which every column is discrete.
    #
    # @param sample_prior The prior equivalent sample size.
    # @param structure_prior The structure prior; 0 for none.
    use_bdeu = function(sample_prior = 10, structure_prior = 0) {
      .self$.setParamDouble("priorEquivalentSampleSize", sample_prior)
      .self$.setParamDouble("structurePrior", structure_prior)
      .self$.use_score("BdeuScore")
    },

    # Set the score to the Conditional Gaussian BIC score, for data with discrete and continuous columns.
    #
    # @param penalty_discount The penalty discount.
    # @param discretize TRUE if a continuous parent of a discrete child should be discretized, which is faster;
    #   FALSE to integrate over it.
    # @param num_categories_to_discretize How many categories to use when discretizing.
    # @param structure_prior The structure prior; 0 for none.
    # @param min_sample_size_per_cell The smallest discrete cell the likelihood will be fitted in.
    # @param effective_sample_size -1 to use the number of rows; otherwise the score behaves as if the data
    #   had that many independent rows.
    use_conditional_gaussian_score = function(penalty_discount = 1, discretize = TRUE,
                                              num_categories_to_discretize = 3, structure_prior = 0,
                                              min_sample_size_per_cell = 4, effective_sample_size = -1) {
      .self$.setParamDouble("penaltyDiscount", penalty_discount)
      .self$.setParamDouble("structurePrior", structure_prior)
      .self$.setParam("discretize", discretize)
      .self$.setParamInt("numCategoriesToDiscretize", num_categories_to_discretize)
      .self$.setParamInt("minSampleSizePerCell", min_sample_size_per_cell)
      .self$.setParamInt("effectiveSampleSize", effective_sample_size)
      .self$.use_score("ConditionalGaussianBicScore")
    },

    # Set the score to the Degenerate Gaussian BIC score, for data with discrete and continuous columns.
    #
    # @param penalty_discount The penalty discount.
    # @param structure_prior The structure prior; 0 for none.
    # @param singularity_lambda At or above 0, this is added to the diagonal of a covariance matrix before it is
    #   inverted; below 0, a pseudoinverse is used.
    use_degenerate_gaussian_score = function(penalty_discount = 1, structure_prior = 0, singularity_lambda = 0) {
      .self$.setParamDouble("penaltyDiscount", penalty_discount)
      .self$.setParamDouble("structurePrior", structure_prior)
      .self$.setParamDouble("singularityLambda", singularity_lambda)
      .self$.use_score("DegenerateGaussianBicScore")
    },

    # Set the test to Chi Square, for data in which every column is discrete.
    #
    # @param min_count The smallest count a cell of the table may have and still be used.
    # @param alpha The significance cutoff.
    # @param cell_table_type How the counts are made: 1 = AD tree, 2 = by counting the sample. The result is
    #   the same; the speed may differ.
    # @param use_for_mc TRUE to set the Markov checker's test and leave the search's test as it is.
    use_chi_square = function(min_count = 1, alpha = 0.01, cell_table_type = 1, use_for_mc = FALSE) {
      .self$.setParamDouble("alpha", alpha)
      .self$.setParamInt("minCountPerCell", min_count)
      .self$.setParamInt("cellTableType", cell_table_type)
      .self$.use_test("ChiSquare", use_for_mc)
    },

    # Set the test to G Square, for data in which every column is discrete.
    #
    # @param min_count,alpha,cell_table_type,use_for_mc As for use_chi_square.
    use_g_square = function(min_count = 1, alpha = 0.01, cell_table_type = 1, use_for_mc = FALSE) {
      .self$.setParamDouble("alpha", alpha)
      .self$.setParamInt("minCountPerCell", min_count)
      .self$.setParamInt("cellTableType", cell_table_type)
      .self$.use_test("GSquare", use_for_mc)
    },

    # Set the test to the Conditional Gaussian likelihood ratio test, for data with discrete and continuous
    # columns.
    #
    # @param alpha The significance cutoff.
    # @param discretize,num_categories_to_discretize,min_sample_size_per_cell,effective_sample_size As for
    #   use_conditional_gaussian_score.
    # @param use_for_mc TRUE to set the Markov checker's test and leave the search's test as it is.
    use_conditional_gaussian_test = function(alpha = 0.01, discretize = TRUE, num_categories_to_discretize = 3,
                                             use_for_mc = FALSE, min_sample_size_per_cell = 4,
                                             effective_sample_size = -1) {
      .self$.setParamDouble("alpha", alpha)
      .self$.setParam("discretize", discretize)
      .self$.setParamInt("numCategoriesToDiscretize", num_categories_to_discretize)
      .self$.setParamInt("minSampleSizePerCell", min_sample_size_per_cell)
      .self$.setParamInt("effectiveSampleSize", effective_sample_size)
      .self$.use_test("ConditionalGaussianLrt", use_for_mc)
    },

    # Set the test to the Degenerate Gaussian likelihood ratio test, for data with discrete and continuous
    # columns.
    #
    # @param alpha The significance cutoff.
    # @param use_for_mc TRUE to set the Markov checker's test and leave the search's test as it is.
    # @param singularity_lambda As for use_degenerate_gaussian_score.
    use_degenerate_gaussian_test = function(alpha = 0.01, use_for_mc = FALSE, singularity_lambda = 0) {
      .self$.setParamDouble("alpha", alpha)
      .self$.setParamDouble("singularityLambda", singularity_lambda)
      .self$.use_test("DegenerateGaussianLrt", use_for_mc)
    },

    # Runs the PC algorithm.
    #
    # @param conflict_rule Kept for existing calls; PC in the current Tetrad does not read it.
    # @param depth The maximum number of conditioning variables per test.
    # @stable_fas TRUE is the stable FAS should be used. (Before 2026-11-26 this was set under a name Tetrad
    #   does not have, here and in run_fci, so FALSE had no effect.)
    # @guarantee_cpdag Kept for existing calls; PC in the current Tetrad does not read it.
    # @return The estimated graph.
    run_pc = function(conflict_rule=1, depth=-1, stable_fas=TRUE, guarantee_cpdag=FALSE) {
      cat("Running PC algorithm...\n")

      .self$.setParamInt("conflictRule", conflict_rule)
      .self$.setParamInt("depth", depth)
      .self$.setParam("stableFAS", stable_fas)
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

    .setParamLong = function(key, value) {
      .jcall(.self$params, "V", "set", key, .jcast(.jnew("java/lang/Long", .jlong(value)), "java/lang/Object"))
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

    # Run the BOSS Top-K algorithm, which keeps the best few models BOSS comes across and not only the best one.
    #
    # The best graph is the result, as for run_boss: get_java() and print_graph() give it. The models kept, best
    # first, are given by get_topk_graphs(), get_topk_scores() and get_topk_orders(). The first of them is the
    # result.
    #
    # With split_delta = 0 and num_starts = 1 the search is plain BOSS and keeps one model. To get several, set
    # num_starts above 1, or split_delta above 0, or both.
    #
    # Requires a tetrad-current.jar built from development on or after 2026-11-26.
    #
    # @param top_k How many models to keep at most.
    # @param split_delta When above 0, a placement of a variable that scores within this much of the best placement
    #   is set aside and searched from later, as a branch of its own. 0 turns splitting off. The score is the one
    #   set by the use_* method, so for a BIC score this is in BIC units.
    # @param split_defer_ties Whether a placement that ties with the best is set aside too. It gives the same model
    #   but a different order to search from. TRUE takes more runs; FALSE is cheaper. Only read when split_delta is
    #   above 0.
    # @param max_runs A cap on the number of searches made, counting the branches set aside. A search that reaches
    #   the cap stops there, so the models kept are then the best of those reached, not of all there are.
    #   get_topk_num_runs() gives the number made and get_topk_stopped_by_max_runs() says whether the cap cut the
    #   search short.
    # @param dedup_by_cpdag TRUE to count two orders that give the same CPDAG as one model; FALSE to count every
    #   order as a model.
    # @param optimal_across_branches TRUE to offer every order visited to the models kept, not only the order each
    #   search ends at.
    # @param num_starts,use_bes,time_lag,use_data_order,output_cpdag As for run_boss.
    # @param seed The random seed for starts after the first, or -1 for none.
    # @return The best graph, invisibly.
    run_boss_topk = function(top_k = 10, split_delta = 0, split_defer_ties = TRUE, max_runs = 10000,
                             dedup_by_cpdag = TRUE, optimal_across_branches = FALSE, num_starts = 1,
                             use_bes = FALSE, time_lag = 0, use_data_order = TRUE, output_cpdag = TRUE,
                             seed = -1) {
      cat("Running BOSS Top-K algorithm...\n")

      .self$.check_score()

      alg <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.cpdag.BossTopK", .self$score)

      if (!any(grepl("getTopGraphs", .jmethods(alg), fixed = TRUE))) {
        stop("This tetrad-current.jar predates the BOSS Top-K accessors for the models kept; update to a jar ",
             "built from development on or after 2026-11-26.")
      }

      .self$.setParamInt("topK", top_k)
      .self$.setParamDouble("splitDelta", split_delta)
      .self$.setParam("splitDeferTies", split_defer_ties)
      .self$.setParamInt("maxRuns", max_runs)
      .self$.setParam("dedupByCpdag", dedup_by_cpdag)
      .self$.setParam("optimalAcrossBranches", optimal_across_branches)
      .self$.setParam("useBes", use_bes)
      .self$.setParamInt("numStarts", num_starts)
      .self$.setParamInt("timeLag", time_lag)
      .self$.setParam("useDataOrder", use_data_order)
      .self$.setParam("outputCpdag", output_cpdag)
      .self$.setParamLong("seed", seed)

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      .jcall(alg, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(alg, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
      .self$graph <- graph

      graphs <- .jcall(alg, "Ljava/util/List;", "getTopGraphs")
      scores <- .jcall(alg, "Ljava/util/List;", "getTopScores")
      orders <- .jcall(alg, "Ljava/util/List;", "getTopOrders")
      kept <- seq_len(.jcall(graphs, "I", "size"))

      .self$topk_graphs <- lapply(kept, function(i) {
        .jcast(.jcall(graphs, "Ljava/lang/Object;", "get", as.integer(i - 1)), "edu.cmu.tetrad.graph.Graph")
      })
      .self$topk_scores <- vapply(kept, function(i) {
        .jcall(.jcall(scores, "Ljava/lang/Object;", "get", as.integer(i - 1)), "D", "doubleValue")
      }, numeric(1))
      .self$topk_orders <- lapply(kept, function(i) {
        order <- .jcall(orders, "Ljava/lang/Object;", "get", as.integer(i - 1))
        nodes <- .jcall(order, "[Ljava/lang/Object;", "toArray")
        vapply(nodes, function(node) .jcall(node, "S", "getName"), character(1))
      })
      .self$topk_result <- graph

      if (any(grepl("getNumRuns", .jmethods(alg), fixed = TRUE))) {
        .self$topk_num_runs <- .jcall(alg, "I", "getNumRuns")
        .self$topk_stopped <- .jcall(alg, "Z", "isStoppedByMaxRuns")
      } else {
        .self$topk_num_runs <- NA_real_
        .self$topk_stopped <- NA
      }

      cat("BOSS Top-K search completed. Models kept:", length(kept), "\n")
      invisible(.self$graph)
    },

    # Whether the models of the last run_boss_topk still go with the current graph, that is, no other search has
    # replaced its result.
    .topk_current = function() {
      !is(.self$topk_result, "uninitializedField") && !is(.self$graph, "uninitializedField") &&
        .jidenticalRef(.self$graph, .self$topk_result)
    },

    # The graphs of the models kept by the last run_boss_topk, best first, as a list of Java Graph objects. The
    # list is empty if run_boss_topk has not been run or another search has been run since.
    get_topk_graphs = function() {
      if (.self$.topk_current()) .self$topk_graphs else list()
    },

    # The scores of the models kept by the last run_boss_topk, in the order of get_topk_graphs.
    get_topk_scores = function() {
      if (.self$.topk_current()) .self$topk_scores else numeric(0)
    },

    # The variable orders of the models kept by the last run_boss_topk, in the order of get_topk_graphs, each as a
    # character vector of variable names. A model's graph is the one BOSS builds from its order.
    get_topk_orders = function() {
      if (.self$.topk_current()) .self$topk_orders else list()
    },

    # A count from the last run_boss_topk, or the given value if that search has been replaced.
    .topk_count = function(value, none) {
      if (!.self$.topk_current()) return(none)
      if (is.na(value)) {
        stop("This tetrad-current.jar predates the BOSS Top-K run count; update to a jar built from development ",
             "after 2026-11-26.")
      }
      value
    },

    # The number of runs the last run_boss_topk made: its starts, and one for each placement that was set aside
    # and then searched from. With knowledge that puts every variable in a tier this is the sum over the tiers,
    # and max_runs applies to each tier's search separately. It is 0 wherever get_topk_graphs is empty.
    #
    # Requires a tetrad-current.jar built from development after 2026-11-26.
    get_topk_num_runs = function() {
      .self$.topk_count(.self$topk_num_runs, 0)
    },

    # TRUE if max_runs cut the last run_boss_topk short, that is, if a placement that was to be set aside was not
    # searched from because of the cap. The models kept are then the best of those reached, not of all there are
    # within split_delta; raise max_runs to search the rest. A search that used up max_runs exactly, with nothing
    # left set aside, was not cut short. It is FALSE wherever get_topk_graphs is empty.
    #
    # Requires a tetrad-current.jar built from development after 2026-11-26.
    get_topk_stopped_by_max_runs = function() {
      .self$.topk_count(.self$topk_stopped, FALSE)
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
      .self$.setParam("stableFAS", stable_fas)
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
    # @param guarantee_pag Kept for existing calls; not read by BFCI in Tetrad 8.0.0.
    # @param fcit_correctness Warrant for the result (Tetrad 8.0.0): 1 = guarantee I-map (default), 2 = score step,
    #   3 = saturating step.
    # @param imap_alpha Significance level of the I-map gate's tests (default 0.001).
    # @return The estimated graph
    run_bfci = function(depth = -1, max_disc_path_length = -1, complete_rule_set_used = TRUE, guarantee_pag = FALSE,
                        fcit_correctness = 1, imap_alpha = 0.001) {
      cat("Running BFCI algorithm...\n")

      .self$.setParamInt("depth", depth)
      .self$.setParamInt("maxDiscriminatingPathLength", max_disc_path_length)
      .self$.setParam("completeRuleSetUsed", complete_rule_set_used)
      .self$.setParamInt("fcitCorrectness", fcit_correctness)
      .self$.setParamDouble("imapAlpha", imap_alpha)

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      bfci <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.pag.Bfci", .self$test, .self$score)
      .jcall(bfci, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(bfci, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
      .self$graph <- graph

      cat("BFCI search completed.\n")
    },


    # Run the FCI algorithm
    #
    # @param num_starts The number initial random starts for the initial CPDAG search; the one with the best
    #   BIC score is used.
    # @param max_blocking_path_length The maximum length of any blocking path length for the testing phase.
    # @param max_disc_path_length The maximum length of any discriminating path considered, or -1 if unlimited.
    # @param depth The maximum size of any conditioning set for independence testing or -1 if unlimited.
    # @return The estimated graph
    run_fcit = function(num_starts = 1, max_blocking_path_length = 5, depth = 5, max_disc_path_length = -1,
                        starts_with = 1, fcit_correctness = 1, imap_alpha = 0.001) {
      cat("Running FCIT algorithm...\n")

      # Initial Markov PAG: 1 = BOSS, 2 = GRaSP, 3 = SP, 4 = complete PAG
      .self$.setParamInt("fcitStartsWith", starts_with)
      .self$.setParamInt("numStarts", num_starts)

      # FCIT parameters (maxBlockingPathLength is kept for existing calls; FCIT no longer reads it)
      .self$.setParamInt("maxBlockingPathLength", max_blocking_path_length)
      .self$.setParamInt("depth", depth)
      .self$.setParamInt("maxDiscriminatingPathLength", max_disc_path_length)
      .self$.setParamInt("fcitCorrectness", fcit_correctness)
      .self$.setParamDouble("imapAlpha", imap_alpha)

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
    # @param graph                   The graph, as get_java() gives it.
    # @param source                  The name of the source variable.
    # @param target                  The name of the target variable. The sets are for the effect of the source
    #                                on the target.
    # @param graph_type              What kind of graph it is, one of "DAG", "CPDAG", "PDAG", "MPDAG", "MAG" or
    #                                "PAG". It is not worked out from the graph, and it matters: Tetrad treats PAG
    #                                and MAG each in its own way and the others alike, so say "PAG" for the result
    #                                of FCI and its relatives.
    # @param maxNumSets              The maximum number of sets to be adjusted. If this value is less than or equal to
    #                                0, all sets in the target node will be adjusted to match the source node.
    # @param maxDistanceFromEndpoint The maximum distance from the endpoint of the trek to consider for adjustment.
    # @param nearWhichEndpoint       The endpoint(s) to consider for adjustment; 1 = near the source, 2 = near the
    #                                target, 3 = near either.
    # @param maxPathLength           The maximum length of the path to consider for backdoor paths. If a value of -1 is
    #                                given, all paths will be considered.
    # @param henckel_pruning         TRUE to prune each set by the rule of Henckel, Perkovic and Maathuis (2020):
    #                                a variable z is dropped when the target is m-separated from z given the source
    #                                and the rest of the set. This assumes a linear model; the pruned set is still
    #                                valid there and its asymptotic variance is no larger.
    # @param o_set_compatible        TRUE to draw the sets only from the candidates for the O-set: parents of the
    #                                target and of the nodes on the causal paths from the source to it, leaving out
    #                                descendants of the source and other forbidden nodes. FALSE for any valid sets.
    #                                These two are py-tetrad's heckel_pruning (so spelled there) and
    #                                o_set_compatible.
    # @return A list of adjustment sets for the pair of nodes &lt;source, target&gt;. Return an smpty
    # list if source == target or there is no amenable path from source to target.
    get_adjustment_sets = function(graph, source, target, graph_type, max_num_sets = 10,
                                   max_distance_from_point = 5, near_which_endpoint = 1, max_path_length = 20,
                                   henckel_pruning = FALSE, o_set_compatible = FALSE) {
      graph_types <- c("DAG", "CPDAG", "PDAG", "MPDAG", "MAG", "PAG")

      if (missing(graph_type) || !is.character(graph_type) || length(graph_type) != 1 ||
          !(toupper(graph_type) %in% graph_types)) {
        stop("graph_type must be given, as one of ", paste(graph_types, collapse = ", "),
             "; for example get_adjustment_sets(graph, \"X\", \"Y\", graph_type = \"CPDAG\").")
      }

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
                          toupper(graph_type),
                          as.integer(max_num_sets),
                          as.integer(max_distance_from_point),
                          as.integer(near_which_endpoint),
                          as.integer(max_path_length),
                          isTRUE(henckel_pruning),
                          isTRUE(o_set_compatible))


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
    # @param fraction_resample Tests are done using random subsamples of the data per test, if this is
    #   less than 1, or all of the data, if it is equal to 1.
    # @param condition_set_type The type of conditioning set to use for the Markov check, one of:
    #   ORDERED_LOCAL_MARKOV_PROPERTY, ORDERED_LOCAL_MARKOV_PROPERTY_SINK_ELIMINATION, PAIRWISE_MARKOV_PROPERTY,
    #   MARKOV_BLANKET, RECURSIVE_BLOCKING, RECURSIVE_BLOCKING_WITH_GRAPHOID_CLOSURE,
    #   RECURSIVE_BLOCKING_WITH_COMPOSITIONAL_GRAPHOID_CLOSURE, LOCAL_MARKOV, PARENTS_AND_NEIGHBORS or
    #   GLOBAL_MARKOV. These are the names Tetrad now has; a name it does not have is refused with the list of
    #   those it does.
    # @param find_smallest_subset Whether to find the smallest subset for a given set that yields independence.
    # @param parallelized TRUE if conditional independencies should be checked in parallel.
    # @effective_sample_size The effective sample size to use for calculations, or -1 if the actual sample size.
    #   The test must be one that takes an effective sample size.
    # @return Marov checker statistics as a named list.
    markov_check = function(graph, fraction_resample = 1, condition_set_type = "ORDERED_LOCAL_MARKOV_PROPERTY",
                            find_smallest_subset = FALSE, parallelized = TRUE, effective_sample_size = -1) {
      cat("Running Markov check...\n")

      # A field that was never set is not NULL.
      if (is.null(.self$mc_test) || is(.self$mc_test, "uninitializedField")) {
        stop("A test for the Markov Checker has not been set. Please call a `use_*` method with `use_for_mc = TRUE`.")
      }

      # The conditioning set types this Tetrad has, asked of Tetrad so that the list here cannot go stale.
      set_types <- .jcall("edu.cmu.tetrad.search.ConditioningSetType",
                          "[Ledu/cmu/tetrad/search/ConditioningSetType;", "values")
      set_type_names <- vapply(set_types, function(t) .jcall(t, "S", "name"), character(1))

      if (!is.character(condition_set_type) || length(condition_set_type) != 1 ||
          !(condition_set_type %in% set_type_names)) {
        stop("condition_set_type must be one of ", paste(set_type_names, collapse = ", "), ", and was ",
             paste(format(condition_set_type), collapse = " "), ".")
      }

      condition_set_type_ <- set_types[[match(condition_set_type, set_type_names)]]

      dataModel <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")

      test_ <- .jcall(.self$mc_test, "Ledu/cmu/tetrad/search/test/IndependenceTest;",
                     "getTest", dataModel, .self$params)

      mc <- .jnew("edu.cmu.tetrad.search.MarkovCheck", graph, test_, condition_set_type_)

      # Configure it
      .jcall(mc, "V", "setFractionResample", as.double(fraction_resample))
      .jcall(mc, "V", "setFindSmallestSubset", find_smallest_subset)
      .jcall(mc, "V", "setParallelized", parallelized)

      # Set the effective sample size if specified. This has to come before the results are generated: set
      # afterward, as it was here, it changed nothing, since every p-value had been computed by then.
      if (effective_sample_size != -1) {
        .jcall(mc, "V", "setEffectiveSampleSize", as.integer(effective_sample_size))
      }

      # Generate results
      .jcall(mc, "V", "generateAllResults")
      .self$mc_ind_results <- .jcall(mc, "Ljava/util/List;", "getResults", TRUE)

      # Extract statistics
      ad_ind <- .jcall(mc, "D", "getAndersonDarlingP", TRUE)
      ad_dep <- .jcall(mc, "D", "getAndersonDarlingP", FALSE)
      ks_ind <- .jcall(mc, "D", "getKsPValue", TRUE)
      ks_dep <- .jcall(mc, "D", "getKsPValue", FALSE)
      bin_indep <- .jcall(mc, "D", "getBinomialPValue_", TRUE)
      bin_dep <- .jcall(mc, "D", "getBinomialPValue_", FALSE)
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
    # A column of type 'numeric' (double) is continuous. A column of type 'factor', 'character' or 'logical' is
    # discrete: its categories are its levels, or its distinct values in sorted order, by name, and each value is
    # stored as the place of its category, counting from 0 as Tetrad does. A level with no rows is left out. A
    # missing value (NA) stays missing in either kind of column.
    #
    # A column of type 'integer' is continuous unless int_as_cont is FALSE, in which case it is discrete, with
    # its distinct values as the categories. The default is TRUE because read.table and read.csv give type
    # 'integer' to any column of whole numbers, a count or a year as much as a code. To have one such column
    # discrete, make it a factor.
    #
    # (This differs from py-tetrad's pandas_data_to_tetrad, where int_as_cont is FALSE unless given.)
    #
    # @param df The R data frame to translate.
    # @param int_as_cont TRUE to take columns of type 'integer' as continuous; FALSE to take them as discrete.
    data_frame_to_tetrad_dataset = function(df, int_as_cont = TRUE) {
      stopifnot(require(rJava))

      nrows <- nrow(df)
      ncols <- ncol(df)

      # Create Java ArrayList<Node>
      var_list <- .jnew("java/util/ArrayList")

      # Prepare empty double[][] and int[][] (as Java arrays)
      cont_data <- vector("list", ncols)
      disc_data <- vector("list", ncols)

      # Tetrad's code for a missing discrete value, DiscreteVariable.MISSING_VALUE.
      missing_discrete <- -99L

      for (j in seq_len(ncols)) {
        name <- colnames(df)[j]
        col <- df[[j]]

        # A factor is of type integer underneath, and is.numeric is TRUE of an integer column, so the kinds
        # are told apart in this order.
        if (is.factor(col) || is.character(col) || is.logical(col) || (is.integer(col) && !int_as_cont)) {
          levels_ <- if (is.factor(col)) droplevels(col) else factor(col)
          categories <- .jnew("java/util/ArrayList")

          for (category in levels(levels_)) {
            .jcall(categories, "Z", "add", .jcast(.jnew("java/lang/String", category), "java/lang/Object"))
          }

          codes <- as.integer(levels_) - 1L
          codes[is.na(codes)] <- missing_discrete

          variable <- .jnew("edu/cmu/tetrad/data/DiscreteVariable", name, .jcast(categories, "java/util/List"))
          node <- .jcast(variable, "edu/cmu/tetrad/graph/Node")
          .jcall(var_list, "Z", "add", .jcast(node, "java/lang/Object"))
          cont_data[[j]] <- .jnull("[D")  # null double[] for continuous
          disc_data[[j]] <- .jarray(codes, dispatch = TRUE)
        } else if (is.numeric(col)) {
          variable <- .jnew("edu/cmu/tetrad/data/ContinuousVariable", name)
          node <- .jcast(variable, "edu/cmu/tetrad/graph/Node")
          .jcall(var_list, "Z", "add", .jcast(node, "java/lang/Object"))
          cont_data[[j]] <- .jarray(as.numeric(col), dispatch = TRUE)
          disc_data[[j]] <- .jnull("[I")  # null int[] for discrete
        } else {
          stop(paste0("Unsupported column type for ", name, ": ", paste(class(col), collapse = ", "),
                      ". A column must be numeric, integer, factor, character or logical."))
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
