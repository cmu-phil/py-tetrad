## For purposes of these example scripts, we will assume that in RStudio one
## has loaded the py-tetrad directory as the project, so that the project
## directory is the py-tetrad/pytetrad directory. For your own scripts, these 
## paths can be adjusted.
if (!requireNamespace("here", quietly = TRUE)) {
  install.packages("here")
}

library(here)
project_root <- here()
setwd(project_root)

install.packages(reticulate)
install.packages(psych)
install.packages(DiagrammeR)

library(reticulate)

data <- read.table("pytetrad/resources/airfoil-self-noise.continuous.txt",
                   header=TRUE)
i <- c(1, 6)
data[ , i] <- apply(data[ , i], 2, function(x) as.numeric(x))

library(psych)
pairs.panels(data, method = "pearson") 

source_python("pytetrad/tools/TetradSearch.py")
ts <- TetradSearch(data)

ts$add_to_tier(1, "Attack")
ts$add_to_tier(1, "Chord")
ts$add_to_tier(1, "Velocity")
ts$add_to_tier(1, "Displacement")
ts$add_to_tier(1, "Frequency")
ts$add_to_tier(2, "Pressure")

ts$use_sem_bic(penalty_discount=2)
ts$use_fisher_z()
ts$run_grasp()

print(ts$get_string())

library(DiagrammeR)
dot <- ts$get_dot()
grViz(dot)

ts$set_bootstrapping(numberResampling = 30)
ts$run_grasp()
dot <- ts$get_dot()
grViz(dot)
