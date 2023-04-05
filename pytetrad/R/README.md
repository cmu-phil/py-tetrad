# Installation Instructions

This is a possible way of connecting Tetrad to R which we are trying out. If you try the instructions and have trouble, please let us know. 

We have worked out these instructions using RStudio on a Mac; we will test on other platforms soon.

These algorithms output graphs in the PCALG general graph format. For the PCALG general graph format, see the docs for FCI in the PCALG package:

* 0 means NO endpoint
* 1 means CIRCLE endpoint (-o)
* 2 means ARROW endpoint (->)
* 3 means TAIL endpoint (--)

So for X-->Y, the output matrix G, where the index of X is i and the index of Y is j, would have G[j][i] = 3 and G[i][j] = 2.

There are currently several steps need to do the installation. (The instructions will hopefully simplify in the future.)

#### (1) Install a Java JDK. the minimal version for this install is 1.8 (version 8).

For very verbose instructions, see [here](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

#### (2) Install Python. The minimal version for this install is 3.7.

If you're using a version lower than 3.7, [update it](https://www.pythoncentral.io/how-to-update-python/). 

#### (3) Find your Java and Python installation paths.

Open a Terminal window and type:
```
which java
which python
```
Remember these paths for steps below.

#### (4) If you're on a Mac, in a text editor, set JAVA_HOME to your Java installation path in ~/.bash_profile.

On Windows, This step should be unnecessary; check your registry to make sure JAVA_HOME is set. The Java installation should have taken care of this.

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

(Here are docs for [causal learn](https://causal-learn.readthedocs.io/en/latest/), [JPype](https://jpype.readthedocs.io/en/latest/index.html), and [git](https://git-scm.com/doc).

Finally, launch RStudio _from the command line in this or a new Terminal window_.
```
open -na RStudio
```
#### (6) Now, in RStudio:

Inside RStudio, type the following:
```
install.packages("reticulate")
use_python("[...path...to...your...Python...installation...]")
```
This python path was found in step (3).

This only needs to be done once. 

(Here are the docs for the [Reticulate package in R](https://rstudio.github.io/reticulate/).
 
#### (7) Finally, in RStudio, open one of the example R scripts in the py-tetrad repository and run it.

In RStudio,, open the file 'py-tetrad/pytetrad/R/sample_r_code2.R', for example.

Once you've loaded one of the files, adjust the path in it to your working directory if it isn't right already.

Select all lines in the file by typeing control-A.

Then click the Run button. That should run FGES on the example file and print the graph in PCALG general graph format. 

# Some Pointers

Feel free to select a different algorithm or a different test or score in the script. On a Mac, once you've run the script once, look at the line in the script where it says:

g = ts$run_fges()

Here, position your mouse to right right of the '$' sign and on the keyboard type control-Space. This will bring up a list of algorithms you can run, and you can select one. 

Similarly for tests or scores. Some algorithms use just a score, like FGES; others use just a test, like PC; others still use both a test and a score, like GFCI. Which test or score you choose will depend on the type of data you have. We give examples files 'sample_r_code2.R', 'sample_r_code3.R', and 'sample_r_code4.R', which show how to run a search on continuous, discrete, and mixed continuous/discrete data, respectively. If you choose badly, it will tell you.

As shown in the script, you can set background knowledge as indicated. Knowledge is organized into temporal tiers, where variables in later tiers cannot cause variables in earlier tiers, though explicit forbidden or required edges can also be set. Some algorithms do not us knowledge. For these algorithms, if you provide knowledge, they will complain.

Enjoy. 

If you have questions or need more (or different) functionality, [let us know](https://github.com/cmu-phil/py-tetrad/issues). This is literally a brand-new project as of 2023-04-04, so feedback is very welcome.


