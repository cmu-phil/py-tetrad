## This is an example of a script to use rJava to run BOSS on some loaded
## data. The script starts by downloading a local version of Java so that
## the user doesn't need to install Java. JAVA_HOME is set, and rJava is
## initiated. A list of continuous variables is constructed for the the
## columns in the dataset, and the sample size is retrieved. Using this
## information, a CovarianceMatrix is constructed, and this is used to
## constructed a SemBicScore. The SemBicScore is then used to construct
## an instance of BOSS and a PermutationSearch, and the algorithm is run,
## returning a Graph. This graph is then converted into .dot format and
## displayed.
##
## jdramsey 2025-4-14
##
## This may be moved to a separate repository at some point.
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
source("pytetrad/R/TetradSearch.R")

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

print("========== LOADING SMALL DATASET =======")

data <- read.table("pytetrad/resources/airfoil-self-noise.continuous.txt", header=TRUE)

## The read.table function will read decimal columns as real ('numeric')
## and integer columns as discrete. When passing data from R into JAVA,
## integer columns will still be interpreted as discrete, so we have to
## specify in the data frame for this data in columns 1-5 are to be interpreted
## as continuous (i.e., 'numeric'); some of them are integer columns.
i <- c(1, ncol(data))
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))
vars <- create_variables(data)

print("========== RUNNING BOSS ================")

ts <- TetradSearch$new(data)
ts$use_sem_bic()
ts$run_boss()
g2 <- ts$get_java()
ts$print_graph()

print("========== PRINTING BIC =================")

print(g2$getAttribute("BIC"))

print("========== ADJUSTMENT SETS ==============")

adj_sets <- ts$get_adjustment_sets(g2, "Attack", "Pressure")
ts$print_adjustment_sets(adj_sets)

print("========== MARKOV CHECK ==================")

ts$use_fisher_z(use_for_mc=TRUE)
ret <- ts$markov_check(g2)
print(ret)

print("========== LOADING LARGE DATASET ==========")

data <- read.table("pytetrad/resources/example_sim_100-2-1000.txt", header=TRUE)
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))
vars <- create_variables(data)

ts <- TetradSearch$new(data)

print("========== RUNNING ALGORITHM ============")

ts$use_sem_bic()
ts$use_fisher_z()
ts$run_boss()
g4 <- ts$get_java()
print(g4)

print("========== MARKOV CHECK ==================")

ts$use_fisher_z(use_for_mc=TRUE)
ret <- ts$markov_check(g4, condition_set_type="ORDERED_LOCAL_MARKOV")
print(ret)

