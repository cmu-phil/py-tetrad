 We're working out instructions for running this in RStudio.

 For Mac, it's seems necessary to start RStudio from the command line.
 Also, if you change the Python scripts you're importing and want to
 re-import them, you may have to quit RStudio and restart it; for some
 reason reticulate seems to be unable to forget previous imports.

 Set JAVA_HOME to the location of Java, preferably in .bash_profile
 and install RStudio if it's not already

 Also, install py-tetrad using directions in the README for this package.
 Then in terminal:

 > open -na RStudio

 You will need to adjust this path to your path for py-tetrad.
setwd("~/py-tetrad/pytetrad")