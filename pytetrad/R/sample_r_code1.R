## This file shows how to run a script in Python entirely from R
## and store all of the variable results in the R environment, using
## the 'source_python' command in reticulate. This doesn't involve any
## interaction with Python other than to run the script and get back all
## of the results, but some users may like this way of doing it.

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
source_python("run_continuous.py")
tr <- import("pytetrad.tools.translate")

g<-tr$tetrad_graph_to_pcalg(grasp_graph)
g

## All of the variables in this file appear in the R environment and can be
## accessed there.