## This is some sample code for running py-tetrad in R. Works but
## not finished. JR 2023/4/2

library(reticulate)
setwd("/Users/josephramsey/py-tetrad/pytetrad")
tr <- import("tools.translate")
source_python("run_continuous.py")
g<-tr$tetrad_graph_to_pcalg(grasp_graph)
g
