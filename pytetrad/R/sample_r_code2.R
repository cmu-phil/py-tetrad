## This is some sample code for running py-tetrad in R. Works but
## not finished. JR 2023/4/2

## For Mac, it's necessary to start RStudio from the command line, like this:
## First, set JAVA_HOME to the location of Java, preferably in .bash_profile
## and install RStudio if it's not already.
## Also, install py-tetrad using directions in the README for this package.
## Then in terminal:
## > open -na RStudio

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
g <- rs$fges(data, penalty_discount = 2)
g