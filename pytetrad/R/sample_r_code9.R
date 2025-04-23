## This file shows how to Tetrad searches for continuous data interactively 
## in R using the TetradSearch class.
##
## Please make your own copy of this R file if you want to make sure your
## changes don't get overwritten by future `git pull's.
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

library(reticulate)

data <- read.table("pytetrad/resources/airfoil-self-noise.continuous.txt", header=TRUE)

## The read.table function will read decimal columns as real ('numeric')
## and integer columns as discrete. When passing data from R into Python,
## integer columns will still be interpreted as discrete, so we have to
## specify in the data frame for this data in columns 1-5 are to be interpreted
## as continuous (i.e., 'numeric'); some of them are integer columns.
i <- c(1, 6)
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

## Make a TetradSearch object.
source_python("pytetrad/tools/TetradSearch.py")
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


ts$run_boss()

# Here we show how to use the Markov checker
ts$use_fisher_z(0.05, use_for_mc=TRUE)
results = ts$markov_check(ts$get_java())

# Returns ad_ind, ad_dep, bin_indep, bin_dep, frac_dep_ind, frac_dep_dep, num_tests_ind, num_tests_dep
print(results)

print(ts$all_subsets_independence_facts(ts$get_java()))



