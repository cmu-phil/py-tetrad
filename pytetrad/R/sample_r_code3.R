## This file shows how to Tetrad searches interactively in R using the
## TetradSearch class for a discrete example.
##
## Please make your own copy of this R file if you want to make sure your
## changes don't get overwritten by future `git pull's.
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

library(reticulate)

## It's best to change hyphens and periods in variable names to underscores
## for reading data into R.
data <- read.table("./resources/bridges.data.version211_rev.txt", header=TRUE)

# ## The read.table function will read decimal columns as real ('numeric')
# ## and integer columns as discrete. When passing data from R into Python,
# ## integer columns will still be interpreted as discrete, so we have to
# ## specify in the data frame for this data that they are to be interpreted
# ## as continuous (i.e., 'numeric').
#  i <- c(1, 6)
#  data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

## Make a TetradSearch object.
source_python("tools/TetradSearch.py")
ts <- TetradSearch(data)

## Use the SEM BIC score.
ts$use_bdeu()
ts$use_g_square()

# RIVER	ERECTED	PURPOSE	LENGTH	LANES	CLEAR_G	T_OR_D	MATERIAL	SPAN	REL_L	TYPE

## Set some knowledge--let's try to predict TYPE
ts$add_to_tier(0, "RIVER")
ts$add_to_tier(0, "ERECTED")
ts$add_to_tier(0, "PURPOSE")
ts$add_to_tier(0, "LENGTH")
ts$add_to_tier(0, "LANES")
ts$add_to_tier(0, "CLEAR_G")
ts$add_to_tier(0, "T_OR_D")
ts$add_to_tier(0, "MATERIAL")
ts$add_to_tier(0, "SPAN")
ts$add_to_tier(0, "REL_L")
ts$add_to_tier(1, "TYPE")

## Run the search and return the graph in PCALG format
ts$run_grasp()

## Print the graph and grab the DOT format string (for Grasphviz)
print(ts$get_string())
dot <- ts$get_dot()

## Plot matrix of variables to show evil distributions.
# library(psych)
# pairs.panels(data, method = "pearson") # correlation method hist.col = "#00AFBB", density = TRUE, # show density plots ellipses = TRUE # show correlation ellipses )

## Allows RStudio to render graphs in the Viewer window.
library('DiagrammeR')
grViz(dot)