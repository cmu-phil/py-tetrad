## This file shows how to run a script in Python entirely from R
## and store all of the variable results in the R environment, using
## the 'source_python' command in reticulate. This doesn't involve any
## interaction with Python other than to run the script and get back all
## of the results, but some users may like this way of doing it.
##
## The secret is that when you do it this way, any Java data set or graph
## can be converted into R data frames using the 'translate' commands.
## Any pandas data frame in Python will be immediately usable as a
## data frame in R and will require no further translation. Such
## environment variables can be immediately used in R. Otherwise, 
## translating them into data frames does the trick.
##
## We're working out instructions for running this in RStudio.
##
## For Mac, it's seems necessary to start RStudio from the command line.
## Also, if you change the Python scripts you're importing and want to
## re-import them, you may have to quit RStudio and restart it; for some
## reason reticulate seems to be unable to forget previous imports.
##
## Set JAVA_HOME to the location of Java, preferably in .bash_profile
## and install RStudio if it's not already
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
source_python("run_continuous.py")
tr <- import("pytetrad.tools.translate")

g<-tr$tetrad_graph_to_pcalg(grasp_graph)
g

## All of the variables in this file appear in the R environment and can be
## accessed there. If you're in RStudio, click to the Environment tab and 
## they're all there.