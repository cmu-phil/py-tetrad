## This file shows how to Tetrad searches interactively in R using the
## TetradSearch class.
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

install.packages(reticulate)
library(reticulate)

data <- read.table("./resources/airfoil-self-noise.continuous.txt", header=TRUE)

## The read.table function will read decimal columns as real ('numeric')
## and integer columns as discrete. When passing data from R into Python,
## integer columns will still be interpreted as discrete, so we have to
## specify in the data frame for this data that they are to be interpreted
## as continuous (i.e., 'numeric').
 i <- c(1, 6)
 data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

## Make a TetradSearch object.
source_python("tools/TetradSearch.py")
ts <- TetradSearch(data)

## Use the SEM BIC score.
ts$use_sem_bic(penalty_discount=2)
ts$use_fisher_z()

## Set some knowledge.
ts$add_to_tier(1, "Frequency")
ts$add_to_tier(1, "Attack")
ts$add_to_tier(1, "Chord")
ts$add_to_tier(2, "Velocity")
ts$add_to_tier(2, "Displacement")
ts$add_to_tier(2, "Pressure")

## Run the search and return the graph in PCALG format
g = ts$run_fges()

## Print the graph in PCALG general graph format (see PCALG's FCI docs)
print(g)