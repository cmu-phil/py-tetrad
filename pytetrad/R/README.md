## Instructions for setting up Tetrad searches to run in R (RStudio) via Py-Tetrad

The minimal requirements for Java and Python for this particular setup are Java 1.8+ (8+), Python 3.7+. Not sure the minimal requirements for RStudio and R. In any case, using the latest stable versions of all of these will work.

We will assume for purposes of this tutorial you're using RStudio on a Mac; we will test on other platforms soon.

There are currently several steps need to do the installation.

#### (1) Install a Java JDK. Any version 1.8+ (i.e., 8+) will do for this. For very verbose isntrucitons, see [here](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

#### (2) Install Python. Make sure you are using the latest Python--at least 3.7--if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

#### (3) In a text editor, add this line to the file ~/.bash_profile:
```
export JAVA_HOME=[..path..to...your...java...jdk...]
```
and save. If you don't know where your Java JDK is, in a Terminal window type 
```
which java
```
#### (4) In a new Terminal window, do the following:
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

Finally, launch RStudio from the command line.
```
open -na RStudio
```
#### (5) Now, in RStudio:

Install the 'reticulate' package. (This only needs to be done once.)
```
install.packages("reticulate")
```
Here are the [Docs for the Reticulate package](https://rstudio.github.io/reticulate/).

Also, tell Reticulate/R where your Python installation is located. (This also only needs to be done once).
```
use_python("[...path...to...your...Python...installation...]")
```
Here, the Python path should be the path to your Python; you can type 
```
which python
```
in a Terminal window to get this.
 
#### (6) Finally, in RStudio, open one of the example R scripts in the py-tetrad repository you cloned above. In the online GitHub, they're here:

https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/R

Adjust the path in it to your working directory in the script (if it isn't right already), select all, and run. That should run FGES on the example file and print the graph in PCALG general graph format. 

For the PCALG general graph format, see the docs for FCI in the PCALG package:
* 0 means NO endpoint
* 1 means CIRCLE endpoint (-o)
* 2 means ARROW endpoint (->)
* 3 means TAIL endpoint (--)

So for X-->Y, the output matrix G, where the index of X is i and the index of Y is j, would have G[j][i] = 3 and G[i][j] = 2.
