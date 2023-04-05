## Instructions for setting up Tetrad searches to run in R (RStudio) via Py-Tetrad

This is a _tentative project_; if it's not doing the job in a helpful way, we will pursue other options! So, please [let us know](https://github.com/cmu-phil/py-tetrad/issues).
 
The setup requires several steps, and you have to get several paths set right, but the payoff of going through all the setup will be very nice; it will be easy and reliable to run Tetrad algorithms in R. We are not sure yet whether these instuctions can be followed easily; please [give feedback](https://github.com/cmu-phil/py-tetrad/issues) if not.

We will assume for purposes of this tutorial you're using a Mac. If you're using Windows, you might want to wait until we've figured out how to do this on a Windows machine. (Or, figure it out and [tell us how](https://github.com/cmu-phil/py-tetrad/issues)!)

We will also assume that you are using RStudio.

The _minimal_ requirements for Java and Python for this particular setup are Java 1.8+ (8+), Python 3.7+. Not sure the minimal requirements for RStudio and R. (If you know, please [tell us](https://github.com/cmu-phil/py-tetrad/issues)!) In any case, using the latest stable versions of all of these will work.

We are thinking about some kind of packaging for this to make the install process easier, maybe an R package or a Docker perhaps.

We are unsure what kind of graph to output to be useful to R users; currently we are outputting a general graph format used by PCALG. If you have thoughts for this, please [let us know](https://github.com/cmu-phil/py-tetrad/issues).

#### (1) You must follow the instructions in the [py-tetrad README](https://github.com/cmu-phil/py-tetrad) to clone the py-tetrad GitHub repository and set it up (Installing JPype, etc.). It's best to set the JAVA_HOME variable in the .bash_profile file.

We give these instructions below.

* If you don't have one, install a Java JDK. Any version 1.8+ (i.e., 8+) will do for this. For very verbose isntrucitons, see [here](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

* In the file ~/.bash_profile, add this line:

export JAVA_HOME=[..path..to...your...java...jdk...]

and save. If you don't know where you JDK is, in a Terminal window type `which java`.

* Make sure you are using the latest Python--at least 3.7--if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

* In a new Terminal window (to grab the JAVA_HOME you just set), do some pip installs:

pip install causal-learn
pip install JPype1

* Finally, (for instance, on a Mac), in your User direction (~), type the following to clone this repository:
    
```   
git clone https://github.com/cmu-phil/py-tetrad/
cd py-tetrad/pytetrad
python run_continuous.py
```

This last command should cause various algorithms to run in Tetrad and print out result graphs.

#### (2) On a Mac, launch RStudio from your Terminal window.

In your Terminal window:

`
open -na RStudio
`

#### (3) In RStudio, install the 'reticulate' package. (This only needs to be done once.)

`
install.packages("reticulate")
`
Here are the [Docs for the Reticulate package](https://rstudio.github.io/reticulate/).

#### (4) In RStudio, tell Reticulate/R where your Python installation is located. (This also only needs to be done once).

`
use_python("[...path...to...your...Python...installation...]")
`

Here, the Python path should be the path to your Python; you can type `which Python` in a Terminal window to get this.

#### (5) Then if you've done all that, you can open one of the example R scripts in the py-tetrad repository you cloned above. In the online GitHub, they're here:

https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/R

#### (6) Then adjust the path in it to your working directory in the script (if it isn't right already), select all, and run. That should run FGES on the example file and print the graph in PCALG general graph format. 

For the PCALG general graph format, see the docs for FCI in the PCALG package:
* 0 means NO endpoint
* 1 means CIRCLE endpoint (-o)
* 2 means ARROW endpoint (->)
* 3 means TAIL endpoint (--)

So for X-->Y, the output matrix G, where the index of X is i and the index of Y is j, would have G[j][i] = 3 and G[i][j] = 2.
