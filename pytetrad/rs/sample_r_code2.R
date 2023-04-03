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
source_python("run_continuous.py")

g<-tr$tetrad_graph_to_pcalg(grasp_graph)
g

## All of the variables in this file appear in the R environment and can be
## accessed there.