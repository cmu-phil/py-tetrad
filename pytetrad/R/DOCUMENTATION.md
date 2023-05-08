# RPy-Tetrad: Some Initial Documentation

Click here for [Installation Instructions](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/INSTALLATION.md).

The RPyTetrad project is an R interface for the search algorithms in the [Tetrad](https://github.com/cmu-phil/tetrad) package. This page will eventualy turn into some bonafide documentation; please be patient. 

For information on specific algorithms, tests, or scores, or if you'd like to watch some videos on causal search, please see the [Documentation Section on the Tetrad GitHub page](https://github.com/cmu-phil/tetrad#documentation). 

if you are familiar with Tetrad, these are the same algorithms, tests, and scores that are available in the Search box in the current Tetrad interface, and in the current Python package [py-tetrad](https://github.com/cmu-phil/py-tetrad), and will work exactly the same way in each case.

These algorithms output graphs in several formats, which we will document. Currently supported graph types are Java object (Tetrad EdgeListGraph), Python object (Causal-learn GeneralGraph), DOT, PCALG, , and Lavaan.

The PCALG general graph format, as R data frames, in particular, is a square edge matrix; see the docs for FCI in the PCALG package. The endpoints are recorded as follows:

* 0 means NO endpoint
* 1 means CIRCLE endpoint (-o)
* 2 means ARROW endpoint (->)
* 3 means TAIL endpoint (--)

So for X-->Y, the output matrix G, where the index of X is i and the index of Y is j, would have G[j][i] = 3 and G[i][j] = 2.

We will assume that you are working in RStudio and that you've just run the following script from the installation instructions: 'py-tetrad/pytetrad/R/sample_r_code2.R'. Here is that script:
```
## This file shows how to Tetrad searches for continuous data interactively 
## in R using the TetradSearch class.
##
## Please make your own copy of this R file if you want to make sure your
## changes don't get overwritten by future `git pull`'s.
##
## You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")

install.packages(reticulate)
library(reticulate)

data <- read.table("./resources/airfoil-self-noise.continuous.txt", header=TRUE)

## The read.table function will read decimal columns as real ('numeric')
## and integer columns as discrete. When passing data from R into Python,
## integer columns will still be interpreted as discrete, so we have to
## specify in the data frame for this data in columns 1-5 are to be interpreted
## as continuous (i.e., 'numeric'); some of them are integer columns.
i <- c(1, 6)
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

## Make a TetradSearch object.
source_python("tools/TetradSearch.py")
ts <- TetradSearch(data)

## Set some knowledge--we know pressure should be the endogenous variable
## here, so why not help the search out? (It's interesting of course to
## see what searches can get this right without the help.)
ts$add_to_tier(1, "Frequency")
ts$add_to_tier(1, "Attack")
ts$add_to_tier(1, "Chord")
ts$add_to_tier(1, "Velocity")
ts$add_to_tier(1, "Displacement")
ts$add_to_tier(2, "Pressure")

## Run the search and return the graph in PCALG format
ts$use_sem_bic(penalty_discount=2)
ts$use_fisher_z(0.05)
ts$run_fges()

## Print the graph and grab the DOT format string (for Grasphviz)
print(ts$get_string())
dot <- ts$get_dot()

## Plot matrix of variables to show evil distributions.
# library(psych)
# pairs.panels(data, method = "pearson") # correlation method hist.col = "#00AFBB", density = TRUE, # show density plots ellipses = TRUE # show correlation ellipses )

## Allows RStudio to render graphs in the Viewer window.
library('DiagrammeR')
grViz(dot)
```
After you've run the script once, look at the line in the script where it says:
```
ts$run_fges()
```
Here, in RStudio, position your mouse to right right of the '$' sign and on the keyboard type control-Space. This will bring up a list of algorithms you can run, and you can select a different algorithm if you like. 

Similarly for tests or scores; you can select different tests or scores using the same method. There are some considerations. Some algorithms use just a score, like FGES; others use just a test, like PC; others still use both a test and a score, like GFCI. If you provide the wrong options, it will tell you.

Also, which test or score you choose will depend on the type of data you have. We give examples files 'sample_r_code2.R', 'sample_r_code3.R', and 'sample_r_code4.R', which show how to run a search on continuous, discrete, and mixed continuous/discrete data, respectively. If you choose badly, it will tell you.

You may also select graph output types in the same fashion.

As shown in the script, you can set background knowledge as indicated. Knowledge is organized into temporal tiers, where variables in later tiers cannot cause variables in earlier tiers, though explicit forbidden or required edges can also be set. Some algorithms do not use knowledge; if you provide knowledge and the algorithm you choose can't use it, it will tell you.


