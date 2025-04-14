# This class translates some select methods from TetradSearch.py in py-tetrad
# for use in R using rJava.

TetradSearch <- setRefClass(
  "TetradSearch",

  fields = list(
    data = "data.frame",          # Input dataset
    sample_size = "numeric",      # Sample size
    vars = "ANY",                 # Variables for the covariance matrix
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

      i <- c(1, ncol(data))
      data[, i] <<- apply(data[, i], 2, as.numeric)
      .self$vars <- create_variables(data)

      # .self$data_model <- .jnew("edu/cmu/tetrad/data/CovarianceMatrix",
      #                    .self$vars,
      #                    .jarray(as.matrix(cov(data)), dispatch = TRUE),
      #                    as.integer(.self$sample_size))
      #
      .self$data_model <- .self$convert_to_mixed_dataset(data)
      .self$data_model <- .jcast(.self$data_model, "edu.cmu.tetrad.data.DataModel")


      cat("Covariance matrix created.\n")

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
    # @return The resulting graph from the FGES algorithm.
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

    # --- Run BOSS using algcomparison wrapper ---

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
    # @return The resulting graph from the FCI algorithm.
    run_fci = function(depth = -1, stable_fas = TRUE, max_disc_path_length = -1, complete_rule_set_used = TRUE, guarantee_pag = FALSE) {
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
    # @return The resulting graph from the BFCI algorithm.
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


    # Run the FCIT algorithm
    #
    # @return The resulting graph from the BFCI algorithm.
    run_fcit = function(num_starts = 1, max_blocking_path_length = 5, depth = 5, max_disc_path_length = 5, guarantee_pag = TRUE) {
      cat("Running FCIT algorithm...\n")

      # BOSS parameters
      .self$.setParamInt("numStarts", num_starts)

      # FCIT parameters
      .self$.setParamInt("maxBlockingPathLength", max_blocking_path_length)
      .self$.setParamInt("depth", depth)
      .self$.setParamInt("maxDiscriminatingPathLength", max_disc_path_length)
      .self$.setParam("guaranteePag", guarantee_pag)

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

    # Print the resulting graph
    #
    # This method prints the structure of the resulting graph.
    # @param graph A Tetrad graph object.
    # @return The graph object.
    print_graph = function() {
      cat("Attempting to print the graph...\n")
      if (is.null(.self$graph)) {
        cat("No graph generated yet. Please run an algorithm first.\n")
      } else {
        cat("Graph structure:\n", .self$graph$toString(), "\n")
      }
      invisible(.self$graph)
    },

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

    markov_check = function(graph, percent_resample = 1, condition_set_type = "ORDERED_LOCAL_MARKOV",
                            remove_extraneous = FALSE, parallelized = TRUE, sample_size = -1) {
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
      .jcall(mc, "V", "setFindSmallestSubset", remove_extraneous)
      .jcall(mc, "V", "setParallelized", parallelized)
      .jcall(mc, "V", "setSetType", condition_set_type_)

      # if (!is.null(.self$knowledge)) {
      #   .jcall(mc, "V", "setKnowledge", .self$knowledge)
      # }

      # Generate results
      .jcall(mc, "V", "generateAllResults")
      .self$mc_ind_results <- .jcall(mc, "Ljava/util/List;", "getResults", TRUE)

      # print(.self$mc_ind_results)

      # Set sample size if specified
      if (sample_size != -1) {
        .jcall(mc, "V", "setSampleSize", as.integer(sample_size))
      }

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

    # Generalized function to create a variable list for tabular (mixed) data
    # Returns a Java ArrayList<Variable>
    create_variables_mixed = function(data) {

      cat("Creating variable list from mixed data...\n")

      var_list <- .jnew("java/util/ArrayList")

      for (name in colnames(data)) {
        col <- data[[name]]

        if (is.numeric(col)) {
          cat("Adding continuous variable:", name, "\n")
          variable <- .jnew("edu/cmu/tetrad/data/ContinuousVariable", name)
        } else if (is.integer(col) || is.factor(col)) {
          num_categories <- length(unique(na.omit(col)))
          cat("Adding discrete variable:", name, "with", num_categories, "categories.\n")
          variable <- .jnew("edu/cmu/tetrad/data/DiscreteVariable", name, as.integer(num_categories))
        } else {
          stop(paste("Unsupported column type for variable:", name))
        }

        .jcall(var_list, "Z", "add", .jcast(variable, "edu/cmu/tetrad/data/Variable"))
      }

      return(var_list)
    },

    convert_to_mixed_dataset = function(df) {
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
