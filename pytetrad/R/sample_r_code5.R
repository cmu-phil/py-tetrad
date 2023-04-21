## This file shows how to Tetrad searches for a large linear Gaussian data set.
##
## Please make your own copy of this R file if you want to make sure your
## changes don't get overwritten by future `git pull's.
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

library(reticulate)

## This in example of linear, Gaussian data with 100 nodes, average degree 6,
## N = 1000
data <- read.table("./resources/example_sim_100-6-1000.txt", header=TRUE)

## Make a TetradSearch object.
source_python("tools/TetradSearch.py")
ts <- TetradSearch(data)

## Use the SEM BIC score.
ts$use_sem_bic(penalty_discount=1)
ts$use_fisher_z(0.05)

## Run the search and return the graph in PCALG format
ts$run_fges()

## Print the graph and grab the DOT format string (for Grasphviz)
print(ts$get_string())
dot <- ts$get_dot()

## There's no way we can do a plot matrix for this data--too many variables.
## But we can render the graph, which using Graphviz will look like
## spaghetti--trying to think of a better way to render it.

## Allows RStudio to render graphs in the Viewer window.
library('DiagrammeR')
grViz(dot)


