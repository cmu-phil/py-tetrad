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
## jdramsey 2024-8-20
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

## Make some continuous data.

# data <- read.table("pytetrad/resources/airfoil-self-noise.continuous.txt", header=TRUE)
data <- read.table("pytetrad/resources/example_sim_100-6-1000.txt", header=TRUE)

## The read.table function will read decimal columns as real ('numeric')
## and integer columns as discrete. When passing data from R into Python,
## integer columns will still be interpreted as discrete, so we have to
## specify in the data frame for this data in columns 1-5 are to be interpreted
## as continuous (i.e., 'numeric'); some of them are integer columns.
i <- c(1, ncol(data))
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))
vars <- create_variables(data)

# This web site should how to pass a matrix as a double[][] array.
# https://www.rforge.net/rJava/docs/reference/jarray.html

# Get the sample size
sample_size <- nrow(data)

cov <- .jnew("edu/cmu/tetrad/data/CovarianceMatrix", 
             vars, 
             .jarray(as.matrix(data), dispatch = TRUE), 
             as.integer(sample_size))

## Use cov to make a SemBicScore...

score <- .jnew("edu.cmu.tetrad.search.score.SemBicScore", .jcast(cov, "edu.cmu.tetrad.data.ICovarianceMatrix"))
.jcall(score, "V", "setPenaltyDiscount", 2)
.jcall(score, "V", "setLambda", -1)

## Construct a BOSS search and return a Tetrad Graph object.

suborder_search <- .jnew("edu.cmu.tetrad.search.Boss", 
                         .jcast(score, "edu.cmu.tetrad.search.score.Score"))
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