## This file shows how to searches interactively against the current
## R-search.py module in py-tetrad, using R.
##
## This is currently rather limited; you can only run FGES or BOSS using
## the SEM BIC score with a given penalty. Also, we don't yet know how to
## pass knowledge into the algorithms. In Python, using JPype, you can 
## use arbitrary search methods with arbitrary scores, and passing in
## knowledge is easy.
##
## For Mac, it's seems necessary to start RStudio from the command line.
## Also, if you change the Python scripts you're importing and want to
## re-import them, you may have to quit RStudio and restart it; for some
## reason reticulate seems to be unable to forget previous imports.
##
## Set JAVA_HOME to the location of Java, preferably in .bash_profile
## and install RStudio if it's not already.
##
## Also, install py-tetrad using directions in the README for this package.
## Then in terminal:
##
## > open -na RStudio
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

install.packages(reticulate)
library(reticulate)

data <- read.table("./resources/airfoil-self-noise.continuous.txt")

## When passing data from R into Python, integer columns will still
## be interpreted as discrete, so we have to specify in the data frame
## that they are to be interpreted as continuous (i.e., 'numeric').
i <- c(1, 6)
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

rs <- import("tools.R_search")
g1 <- rs$fges(data, penalty_discount = 2)
g1

g2 <- rs$boss(data, penalty_discount = 2)
g2