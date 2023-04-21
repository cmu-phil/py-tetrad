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
##
## Please make your own copy of this R file if you want to make sure your
## changes don't get overwritten by future `git pull's.
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

library(reticulate)
source_python("run_continuous.py")
tr <- import("pytetrad.tools.translate")

## All of the variables in this file appear in the R environment and can be
## accessed there. If you're in RStudio, click to the Environment tab and 
## they're all there.