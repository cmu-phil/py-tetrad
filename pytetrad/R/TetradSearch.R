TetradSearch <- setRefClass(
  "TetradSearch",

  fields = list(
    data = "data.frame",          # Input dataset
    sample_size = "numeric",      # Sample size
    vars = "ANY",                 # Variables for the covariance matrix
    cov = "ANY",                  # Covariance matrix
    score = "ANY",                # Score object
    test = "ANY",                 # IndependenceTest object
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

      .self$cov <- .jnew("edu/cmu/tetrad/data/CovarianceMatrix",
                         .self$vars,
                         .jarray(as.matrix(cov(data)), dispatch = TRUE),
                         as.integer(.self$sample_size))
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
    use_fisher_z = function(alpha = 0.01) {
      .self$.setParamDouble("alpha", alpha)
      .self$test <- .jnew("edu.cmu.tetrad.algcomparison.independence.FisherZ")
      .self$test <- .jcast(.self$test, "edu.cmu.tetrad.algcomparison.independence.IndependenceWrapper")

      cat("Fisher Z object created with alpha set.\n")
    },

    run_pc = function(conflict_rule=1, depth=-1, stable_fas=TRUE, guarantee_cpdag=FALSE) {
      cat("Running PC algorithm...\n")

      .self$.setParamInt("conflictRule", conflict_rule)
      .self$.setParamInt("depth", depth)
      .self$.setParam("stableFas", stable_fas)
      .self$.setParam("guaranteePag", guarantee_cpdag)

      dataModel <- .jcast(.self$cov, "edu.cmu.tetrad.data.DataModel")

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

      dataModel <- .jcast(.self$cov, "edu.cmu.tetrad.data.DataModel")

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

      dataModel <- .jcast(.self$cov, "edu.cmu.tetrad.data.DataModel")

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

      dataModel <- .jcast(.self$cov, "edu.cmu.tetrad.data.DataModel")

      fci <- .jnew("edu.cmu.tetrad.algcomparison.algorithm.oracle.pag.Fci", .self$test)
      .jcall(fci, "V", "setKnowledge", .self$knowledge)

      graph <- .jcall(fci, "Ledu/cmu/tetrad/graph/Graph;", "search", dataModel, .self$params)
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

      dataModel <- .jcast(.self$cov, "edu.cmu.tetrad.data.DataModel")

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

      dataModel <- .jcast(.self$cov, "edu.cmu.tetrad.data.DataModel")

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
    }
  )
)
