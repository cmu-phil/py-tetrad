## This file shows how to Tetrad searches interactively in R using the
## TetradSearch class for a discrete example.
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

install.packages(reticulate)
library(reticulate)

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

# RIVER ERECTED PURPOSE LENGTH LANES CLEAR.G T.OR.D MATERIAL SPAN REL.L TYPE

## Set some knowledge--let's try to predict TYPE
ts$add_to_tier(1, "RIVER")
ts$add_to_tier(1, "ERECTED")
ts$add_to_tier(1, "PURPOSE")
ts$add_to_tier(1, "LENGTH")
ts$add_to_tier(1, "LANES")
ts$add_to_tier(1, "CLEAR.G")
ts$add_to_tier(1, "T.OR.D")
ts$add_to_tier(1, "MATERIAL")
ts$add_to_tier(1, "SPAN")
ts$add_to_tier(1, "REL.L")
ts$add_to_tier(2, "TYPE")

## Run the search and return the graph in PCALG format
ts$run_fges()

## Print the graph in PCALG general graph format (see PCALG's FCI docs)
print('FGES')
print(ts$get_lavaan())