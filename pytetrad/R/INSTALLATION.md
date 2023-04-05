# Installation Instructions

Click here for [Documentation](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/DOCUMENTATION.md).

These are installation instructions for using py-tetrad in RStudio to run algorithms in Tetrad from R.

We have worked out and tested these instructions using RStudio on a Mac; we will test on other platforms soon.

The installation instructions should simplify in the future, but here are the current instructions, which we hope are not too difficult to follow.

#### (1) Install a Java JDK. the minimal version for this install is 1.8 (version 8).

For very verbose instructions, see [here](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

#### (2) Install Python. The minimal version for this install is 3.7.

If you're using a version lower than 3.7, [update it](https://www.pythoncentral.io/how-to-update-python/). 

#### (3) Find your Java and Python installation paths.

If you don't know these, open a Terminal window and type:
```
which java
which python
```
Remember these paths for steps below.

#### (4) If you're on a Mac, in a text editor, set JAVA_HOME to your Java installation path in ~/.bash_profile.

On Windows, This step should be unnecessary; check your registry to make sure JAVA_HOME is set. The Java installation step should have taken care of this.

On a Mac, in a text editor, add this line to the file ~/.bash_profile:
```
export JAVA_HOME=[..path..to...your...java...jdk...]
```
and save the file. This Java path was found in step (3).

#### (5) Open a NEW TERMINAL WINDOW, and do the following:
```
pip install causal-learn
pip install JPype1  
git clone https://github.com/cmu-phil/py-tetrad/
```
To test this the installation, type
```
cd py-tetrad/pytetrad
python run_continuous.py
```
This last command should cause various algorithms to run in Tetrad and print out result graphs.

(Here are docs for [causal learn](https://causal-learn.readthedocs.io/en/latest/), [JPype](https://jpype.readthedocs.io/en/latest/index.html), and [git](https://git-scm.com/doc).)

Finally, launch RStudio _from the command line in this or a new Terminal window_.
```
open -na RStudio
```
(Here are the docs for [RStudio](https://posit.co/download/rstudio-desktop/).)

#### (6) Now, in RStudio:

Inside RStudio, type the following:
```
install.packages("reticulate")
use_python("[...path...to...your...Python...installation...]")
```
This python path was found in step (3).

This only needs to be done once. 

(Here are the docs for the [Reticulate package in R](https://rstudio.github.io/reticulate/).)
 
#### (7) Finally, in RStudio, open one of the example R scripts in the py-tetrad repository and run it.

In RStudio,, open the file 'py-tetrad/pytetrad/R/sample_r_code2.R', for example.

Once you've loaded it, adjust the path in it to the 'py-tetrad/pytetrad' directory if it isn't right already--this line:
```
setwd("~/py-tetrad/pytetrad")
```
Select all lines in the file by typeing control-A.

Then click the Run button. That should run FGES on the example file and print the graph in PCALG general graph format. 
