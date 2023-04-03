## This is some sample code for running py-tetrad in R. Works but
## not finished. JR 2023/4/2

## For Mac, it's necessary to start RStudio from the command line, like this:
## First, set JAVA_HOME to the location of Java, preferably in .bash_profile
## and install RStudio if it's not already.
## Also, install py-tetrad using directions in the README for this package.
## Then in terminal:
## > open -na RStudio

setwd("~/py-tetrad/pytetrad")

install.packages(reticulate)
library(reticulate)

data <- read.table("./resources/airfoil-self-noise.continuous.txt")
i <- c(1, 6) 
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

rs <- import("tools.rsearch")
g <- rs$fges(data)
g
 
