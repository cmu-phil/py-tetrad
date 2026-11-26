## This is an example of a script to use rJava to run IMaGES (BOSS over an
## ImagesScore) on several datasets sharing the same variables. The script
## starts by downloading a local version of Java so that the user doesn't
## need to install Java. JAVA_HOME is set, and rJava is initiated. A single
## list of continuous variables is constructed ONCE and reused for every
## dataset -- this is essential, since ImagesScore requires that all
## component scores share object-identical variables. For each dataset a
## CovarianceMatrix and SemBicScore are constructed; the SemBicScores are
## collected into a java.util.ArrayList and used to construct an
## ImagesScore. The ImagesScore is then used to construct an instance of
## BOSS and a PermutationSearch, and the algorithm is run, returning a
## Graph. This graph is then converted into .dot format and displayed.
##
## jdramsey 2026-7-28
##
## For purposes of these example scripts, we will assume that in RStudio one
## has loaded the py-tetrad directory as the project, so that the project
## directory is the py-tetrad/pytetrad directory. For your own scripts, these
## paths can be adjusted.
if (!requireNamespace("here", quietly = TRUE)) {
  install.packages("here")
}

library(here)
project_root <- here()
setwd(project_root)

print(project_root)

## Install the version of Java I want locally. Set the JAVA_HOME environment
## variables for it so rJava will know to use it.

source("pytetrad/R/my_functions.R")

java_home <- install_local_java(java_dir = "~/local/java/jdk-21.0.12.jdk")
set_java_home(java_home)

if (!requireNamespace("rJava", quietly = TRUE)) {
  install.packages("rJava")
}
library(rJava)

.jinit()
.jaddClassPath("pytetrad/resources/tetrad-current.jar")

print('java version')
java_version <- .jcall("java/lang/System", "S", "getProperty", "java.version")
java_version

## Make some continuous data. For this example we load one dataset and split
## it row-wise into three "datasets" over the same variables; in practice
## these would be separately loaded files with identical column headers in
## identical order.

data <- read.table("pytetrad/resources/example_sim_100-6-1000.txt", header=TRUE)

## Coerce integer-read columns to numeric so all columns are continuous.
i <- c(1, ncol(data))
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

n <- nrow(data)
splits <- split(seq_len(n), cut(seq_len(n), 3, labels = FALSE))
datasets <- lapply(splits, function(idx) data[idx, , drop = FALSE])

## Construct the variable list ONCE. ImagesScore requires that all component
## scores share the same (object-identical) variables, so this same Java
## list is passed to every CovarianceMatrix below. Do NOT call
## create_variables once per dataset.

vars <- create_variables(datasets[[1]])

## Build one SemBicScore per dataset and collect them into a java.util.List.

scores <- .jnew("java/util/ArrayList")

for (d in datasets) {
  cov <- .jnew("edu/cmu/tetrad/data/CovarianceMatrix",
               vars,
               .jarray(as.matrix(d), dispatch = TRUE),
               as.integer(nrow(d)))
  
  score <- .jnew("edu.cmu.tetrad.search.score.SemBicScore",
                 .jcast(cov, "edu.cmu.tetrad.data.ICovarianceMatrix"))
  .jcall(score, "V", "setPenaltyDiscount", 2)
  .jcall(score, "V", "setLambda", -1)
  
  .jcall(scores, "Z", "add", .jcast(score, "java/lang/Object"))
}

## Construct the ImagesScore. NOTE: in the current source the one-argument
## constructor delegates to DATASET_WEIGHTED (its javadoc claims
## SAMPLE_UNIFORM); prefer the explicit two-argument constructor below
## until that is resolved.

# images_score <- .jnew("edu.cmu.tetrad.search.score.ImagesScore",
#                       .jcast(scores, "java/util/List"))

## Alternatively, choose a weighting scheme explicitly. Enum constants are
## static fields, so .jfield retrieves them. DATASET_WEIGHTED rescales each
## component score by (mean N) / N_k so each dataset's vote is independent
## of its sample size; a non-uniform weight schedule may then be set via
## setWeights(double[]).

scheme <- .jfield("edu/cmu/tetrad/search/score/ImagesScore$WeightingScheme",
                  sig = "Ledu/cmu/tetrad/search/score/ImagesScore$WeightingScheme;",
                  "DATASET_WEIGHTED")

images_score <- .jnew("edu.cmu.tetrad.search.score.ImagesScore",
                      .jcast(scores, "java/util/List"),
                      scheme)

## Optionally set a weight schedule over datasets. This is legal ONLY when
## the scheme is DATASET_WEIGHTED; with SAMPLE_UNIFORM (as above) the call
## throws an IllegalStateException. Weights must be positive and finite and
## need not be normalized.
# .jcall(images_score, "V", "setWeights", .jarray(c(1.0, 1.0, 2.0)))

## Construct a BOSS search over the ImagesScore and return a Tetrad Graph.

suborder_search <- .jnew("edu.cmu.tetrad.search.Boss",
                         .jcast(images_score, "edu.cmu.tetrad.search.score.Score"))
.jcall(suborder_search, "V", "setNumStarts", as.integer(5))
perm_search <- .jnew("edu.cmu.tetrad.search.PermutationSearch",
                     .jcast(suborder_search, "edu.cmu.tetrad.search.SuborderSearch"))
graph <- .jcall(perm_search,
                "Ledu/cmu/tetrad/graph/Graph;",
                "search",
                FALSE)

## Convert the graph to DOT format and display it.
dot <- .jcall("edu/cmu/tetrad/graph/GraphSaveLoadUtils",
              "Ljava/lang/String;",
              "graphToDot",
              graph)

library('DiagrammeR')
grViz(dot)