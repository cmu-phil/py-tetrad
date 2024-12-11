# RPy-Tetrad: Installation Instructions

Click here for [Documentation](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/DOCUMENTATION.md).

These are installation instructions for using py-tetrad in RStudio to run algorithms in Tetrad from R.

We have worked out and tested these instructions using RStudio on a Mac; they have been tested (and adjusted) for Windows by end-users. We have not tested them on Linux yet.

Some steps of this installation can be done automatically in the future using a Java package or a Docker container. We apologize for the current complexity.

#### (1) Install a Java JDK. The minimal version for this install is 21.

For very verbose instructions, see [here](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

#### (2) Install Python. The minimal version for this install is 3.5.

If you're using a version lower than 3.7, [update it](https://www.pythoncentral.io/how-to-update-python/). 

#### (3) Find your Java and Python installation paths.

If you don't know which paths you want to use for these already, open a Terminal window and type:
```
which java
which python
```
Remember these paths for the steps below.

#### (4) On a Mac (or maybe Linux too?) Set JAVA_HOME to your Java installation path in the file "~/.Renviron".

On Windows, once you install Java in step (1), this step is unnecessary! Lucky you!

On Mac, in a text editor, check to see if you have a file called `.Renviron` in your home directory, `~`; if not, create one. In this file, type this line, for example--use the path to the Java JDK on your machine that you found in step (3):
```
JAVA_HOME = /Users/[username]/Library/Java/JavaVirtualMachines/[JDK name]/Contents/Home 
```
Save this file as `.Renviron` in your home directory, `~`. Again, this should be the path to the `.../Home` directory of **your** JDK.

Then, when you open RStudio below by double-clicking on its icon after following step 4, step 5 should work. If not, come back to this step and double-check your work.

#### (5) Open a terminal window and type the following:
```
pip install causal-learn
pip install JPype1  
git clone https://github.com/cmu-phil/py-tetrad/
```
To test this installation, type
```
cd py-tetrad/pytetrad
python run_continuous.py
```
This last command should cause various algorithms to run in Tetrad and print out result graphs.

(Here are docs for [JPype](https://jpype.readthedocs.io/en/latest/index.html) and [git](https://git-scm.com/doc).)

#### (6) Now, open RStudio and do some setup there.

Open RStudio, and inside RStudio, type the following:
```
install.packages("reticulate")
install.packages("DiagrammeR")
install.packages("psych")
reticulate::use_python("[...path...to...your...Python...installation...]")
```
For the last command, this may work:
```
reticulate::use_python(Sys.which("python"))
```
This Python path was found in step (3). "DiagrammR" is used in the sample R scripts to render graphs in the RStudio viewer window; if you're running the scripts in command-line R outside of RStudio, it will not help. On Windows, "DiagrammR" must be installed with devtools for the latest R versions. The "psych" package is used in the examples to display scatterplots and histograms of the data.

This only needs to be done once. 

(Here are the docs for [RStudio](https://posit.co/download/rstudio-desktop/), the [Reticulate package in R](https://rstudio.github.io/reticulate/), the [DiagrammeR package in R](https://rich-iannone.github.io/DiagrammeR/), and the [psych package in R](https://www.rdocumentation.org/packages/psych/).)

 
#### (7) Finally, open up RStudio, and in RStudio, open one of the example R scripts in the py-tetrad repository and run it.

In RStudio, open the file 'py-tetrad/pytetrad/R/sample_r_code2.R', for example.

Once you've loaded it, adjust the path to the 'py-tetrad/pytetrad' directory if it isn't right already--this line:
```
setwd("~/py-tetrad/pytetrad")
source("R/sample_r_code2.R")
```
Select all lines in the file by typing control-A.

Then click the Run button. That should run FGES on the example file, display the result in the Viewer window using Graphviz, and display a plot matrix of the scatterplots and histograms of the variables in the Plot window.

We assume you know many other things you can do with data in R if you're an R user.
