# RPyTetrad: Installation Instructions

Click here for [Documentation](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/DOCUMENTATION.md).

These are installation instructions for using py-tetrad in RStudio to run algorithms in Tetrad from R.

We have worked out and tested these instructions using RStudio on a Mac; we will test on other platforms soon.

The installation instructions should simplify in the future; a lot of this will be done automtically in the future using a Java package or Docker. We apologize for the current complexity.

#### (1) Install a Java JDK. the minimal version for this install is 1.8 (version 8).

For very verbose instructions, see [here](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

#### (2) Install Python. The minimal version for this install is 3.7.

If you're using a version lower than 3.7, [update it](https://www.pythoncentral.io/how-to-update-python/). 

#### (3) Find your Java and Python installation paths.

If you don't know which paths you want to use for these already, open a Terminal window and type:
```
which java
which python
```
Remember these paths for steps below.

#### (4) On a Mac (or maybe Linux too?) Set JAVA_HOME to your Java installation path in the file "~/.Renviron".

Apparently on Windows, once you install Java, this step is unnecessary! Lucky you.

<!-- On Windows, This step should be unnecessary; check your registry to make sure JAVA_HOME is set. The Java installation step should have taken care of this.

On a Mac, in a text editor, add this line to the file ~/.bash_profile:
```
export JAVA_HOME=[..path..to...your...java...jdk...]
```
and save the file. This Java path was found in step (3).-->


In the "~/.Renviron file, set JAVA_HOME to the path to your JDK found in step (3). Here's what CHAT GPT says: 

The .Renviron file is used to set environment variables that are specific to R and RStudio. While the basic functionality of the .Renviron file is the same across different operating systems, there are some differences in how the file is used and its location.

On Mac and Linux, the .Renviron file is typically located in the user's home directory, and is used to set environment variables that will be available to R and RStudio. The syntax for setting environment variables in the .Renviron file is:

VARIABLE_NAME=value

For example, to set an environment variable called MY_VARIABLE to a value of hello, you would add the following line to the .Renviron file:

MY_VARIABLE=hello

On Windows, the .Renviron file is located in the user's Documents folder, and is used to set environment variables in the same way as on Mac and Linux. However, the file path and syntax for setting environment variables in the .Renviron file may be different due to differences in the Windows operating system. For example, you may need to use the set command to set environment variables in the .Renviron file on Windows, like this:

set VARIABLE_NAME=value
It's also worth noting that on Windows, the .Renviron file may not be created by default, and you may need to create it yourself.

Regardless of the operating system, any environment variables set in the .Renviron file will be available to R and RStudio, and can be accessed using the Sys.getenv() function in R.

#### (5) Open a terminal window, and type the following:
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

#### (6) Now, open RStudio and do some set up there.

Open RStudio, and inside RStudio, type the following:
```
install.packages("reticulate")
install.packages("DiagrammR")
install.packages("psych")
use_python("[...path...to...your...Python...installation...]")
```
This python path was found in step (3). "DiagrammR" is used in the sample R scripts to render graphs in the RStudio viewer window; if you're running the scripts in command-line R, it will not help. Also, "DiagrammR" needs to be installed with devtools for the latest R versions.

This only needs to be done once. 

(Here are the docs for [RStudio](https://posit.co/download/rstudio-desktop/) and the [Reticulate package in R](https://rstudio.github.io/reticulate/).)
 
#### (7) Finally, in RStudio, open one of the example R scripts in the py-tetrad repository and run it.

In RStudio,, open the file 'py-tetrad/pytetrad/R/sample_r_code2.R', for example.

Once you've loaded it, adjust the path in it to the 'py-tetrad/pytetrad' directory if it isn't right already--this line:
```
setwd("~/py-tetrad/pytetrad")
```
Select all lines in the file by typeing control-A.

Then click the Run button. That should run FGES on the example file and print the graph in PCALG general graph format. 
