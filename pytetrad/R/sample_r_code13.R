##
## This is an example of a script to use rJava to run BOSS Top-K on some
## loaded data, using the TetradSearch class in TetradSearch.R. BOSS Top-K
## keeps the best few models BOSS comes across, not only the best one. The
## script shows how to run it and how to get at the models it kept.
##
## It needs a tetrad-current.jar built from development on or after
## 2026-11-26.
##
## The setup is that of sample_r_code12.R: a local version of Java is
## downloaded so that the user doesn't need to install Java, JAVA_HOME is
## set, and rJava is initiated.
##
## For purposes of these example scripts, we will assume that in RStudio one
## has loaded the py-tetrad directory as the project, so that the project
## directory is the py-tetrad/pytetrad directory. For your own scripts, these
## paths can be adjusted.
##

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
source("pytetrad/R/TetradSearch.R")

java_home <- install_local_java(java_dir = "~/local/java/jdk-21.0.12.jdk")
set_java_home(java_home)

if (!requireNamespace("rJava", quietly = TRUE)) {
  install.packages("rJava")
}

library(rJava)

.jinit()
.jaddClassPath("pytetrad/resources/tetrad-current.jar")

print("========== LOADING DATASET ==============")

data <- read.table("pytetrad/resources/airfoil-self-noise.continuous.txt", header=TRUE)

## All of the columns are to be treated as continuous, so make them all
## 'numeric'; some of them are read as integer columns.
data[] <- lapply(data, as.numeric)

print("========== RUNNING BOSS TOP-K ===========")

ts <- TetradSearch$new(data)
ts$use_sem_bic(penalty_discount = 2)

## With one start and split_delta = 0 this is plain BOSS, and one model is
## kept. Several random starts give several models to keep; the seed makes
## the starts the same from one run of this script to the next. The other
## way to get several is a split_delta above 0, which sets aside every
## placement of a variable that scores within that much of the best one and
## searches from it later.
ts$run_boss_topk(top_k = 5, num_starts = 20, seed = 7)

## The best graph is the result, as for any other search.
print("========== BEST GRAPH ===================")

ts$print_graph()

## The models kept, best first. The first is the best graph above.
print("========== MODELS KEPT ==================")

graphs <- ts$get_topk_graphs()
scores <- ts$get_topk_scores()
orders <- ts$get_topk_orders()

cat("Models kept:", length(graphs), "\n")

for (i in seq_along(graphs)) {
  cat(sprintf("\nModel %d: score %.3f, %.3f from the best\n", i, scores[i], scores[i] - scores[1]))
  cat("Order:", paste(orders[[i]], collapse = ", "), "\n")
  cat(graphs[[i]]$toString(), "\n")
}
