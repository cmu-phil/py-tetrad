## This file shows how to Tetrad searches for continuous data interactively 
## in R using the TetradSearch class.
##
## Please make your own copy of this R file if you want to make sure your
## changes don't get overwritten by future `git pull's.
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

library(reticulate)

data <- read.table("./resources/airfoil-self-noise.continuous.txt", header=TRUE)

## The read.table function will read decimal columns as real ('numeric')
## and integer columns as discrete. When passing data from R into Python,
## integer columns will still be interpreted as discrete, so we have to
## specify in the data frame for this data in columns 1-5 are to be interpreted
## as continuous (i.e., 'numeric'); some of them are integer columns.
i <- c(1, 6)
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

## Make a TetradSearch object.
source_python("tools/TetradSearch.py")
ts <- TetradSearch(data)

## Set some knowledge--we know pressure should be the endogenous variable
## here, so why not help the search out? (It's interesting of course to
## see what searches can get this right without the help.)
ts$add_to_tier(1, "Frequency")
ts$add_to_tier(1, "Attack")
ts$add_to_tier(1, "Chord")
ts$add_to_tier(1, "Velocity")
ts$add_to_tier(1, "Displacement")
ts$add_to_tier(2, "Pressure")

## Run the search and return the graph in PCALG format
ts$use_sem_bic(penalty_discount=2)
ts$use_fisher_z(0.05)
ts$run_fges()

## Print the graph and grab the DOT format string (for Grasphviz)
print(ts$get_string())
dot <- ts$get_dot()

## Plot matrix of variables to show evil distributions.
# library(psych)
# pairs.panels(data, method = "pearson") # correlation method hist.col = "#00AFBB", density = TRUE, # show density plots ellipses = TRUE # show correlation ellipses )

## Allows RStudio to render graphs in the Viewer window.
library('DiagrammeR')
grViz(dot)

