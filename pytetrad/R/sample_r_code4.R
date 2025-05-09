## This file shows how to Tetrad searches interactively in R using the
## TetradSearch class for a mixed example.
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

data <- read.table("pytetrad/resources/auto-mpg.data.mixed.max.3.categories.txt", header=TRUE)

data

## The read.table function will read decimal columns as real ('numeric')
## and integer columns as discrete. When passing data from R into Python,
## integer columns will still be interpreted as discrete, so we have to
## specify in the data frame for this data that they are to be interpreted
## as continuous (i.e., 'numeric').
## Really on the last varaible is discrete; all the other ones are
## continuous... need to fix this.
i <- c(1, 7)
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

## Make a TetradSearch object.
source_python("pytetrad/tools/TetradSearch.py")
ts <- TetradSearch(data)

## Use the SEM BIC score.
ts$use_conditional_gaussian_score(penalty_discount=2)
ts$use_conditional_gaussian_test()

# ts$use_degenerate_gaussian_score()
# ts$use_degenerate_gaussian_test()

#  mpg cylinders displacement horsepower weight acceleration modelyear origin

## Set some knowledge--why not just put mpg in tier 2 and predict it?
ts$add_to_tier(1, "origin")
ts$add_to_tier(1, "cylinders")
ts$add_to_tier(1, "displacement")
ts$add_to_tier(1, "horsepower")
ts$add_to_tier(1, "weight")
ts$add_to_tier(1, "acceleration")
ts$add_to_tier(1, "modelyear")
ts$add_to_tier(2, "mpg")

## Run the search and return the graph in PCALG format
ts$run_boss()

## Print the graph and grab the DOT format string (for Grasphviz)
print(ts$get_string())
dot <- ts$get_dot()

## Plot matrix of variables to show evil distributions.
library(psych)
pairs.panels(data, method = "pearson") 
# correlation method hist.col = "#00AFBB",x density = TRUE, 
# show density plots ellipses = TRUE # show correlation ellipses )

## Allows RStudio to render graphs in the Viewer window.
library('DiagrammeR')
grViz(dot)
