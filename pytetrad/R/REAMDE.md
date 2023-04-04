## Instructions for setting up Tetrad searches to run in R (RStudio) via Py-Tetrad

The setup requires several steps, and you have to get several paths set right, but the payoff of going through all the setup will be very nice. It will be so easy to run Tetrad algorithms in R! We are not sure yet whether these instuctions can be followed easily; please give feedback if not.

We will assume you're using a Mac. If you're using Windows, you might want to wait until we've figured out how to do this on a Windows machine.

We will also assume that you are using RStudio.

##### (1) You must follow the instructions in the [py-tetrad README](https://github.com/cmu-phil/py-tetrad) to clone the py-tetrad GitHub repository and set it up (Installing JPype, etc.). It's best to set the JAVA_HOME variable in the .bash_profile file.

##### (2) Launching RStudio from a Mac's Terminal window would be best. Otherwise, the JAVA_HOME variable doesn't take. ( I haven't tested Windows yet.)

In a Terminal window:

`
open -na RStudio
`

##### (3) You must install the 'reticulate' package in RStudio. (This only needs to be done once.)

`
install.packages("reticulate")
`
Here are the [Docs for the Reticulate package](https://rstudio.github.io/reticulate/).

##### (4) You need to tell Reticulate/R where your Python is in RStudio. (Again, this only needs to be done once).

`
use_python("/usr/local/bin/python")
`

Here, the Python path should be the path to your Python; you can type 'which Python' in a Terminal window to get this.

##### (5) Then if you've done all that, you can open one of the example R scripts in the py-tetrad repository you cloned above. In the online GitHub, they're here:

https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/R

##### (6) Then adjust the path in it to your working directory in the script (if it isn't right already), select all, and run. That should run FGES on the example file and print the graph in PCALG format.

We're still determining whether we're returning a graph compatible with the one in rcausal or whether that matters. We're producing a graph in the PCALG general graph format, as an R data frame.
