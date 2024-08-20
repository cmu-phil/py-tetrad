## RPy-Tetrad: Py-Tetrad for R and RStudio

This project is being offered as a way of connecting Tetrad to R through Python. It is intended to replace the older (less maintainable) [r-causal](https://github.com/bd2kccd/r-causal) Python project that uses an outdated version of Tetrad.

Here are [INSTALLATION INSTRUCTIONS](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/INSTALLATION.md).

Here is some [INITIAL DOCUMENTATION](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/DOCUMENTATION.md).

If you have questions or need more (or different) functionality, or are just flummoxed by the installation procedure, available algorihtms, knowledge functionality, or output graph formats, [let us know](https://github.com/cmu-phil/py-tetrad/issues). Although all of the functionality is from an established project, [Tetrad](https://github.com/cmu-phil/tetrad), this R interface has been available only as of 2023-04-04, so [feedback](https://github.com/cmu-phil/py-tetrad/issues) is very welcome. And thanks for all the feedback we've gotten so far--much appreciated!

## NEWS

* The py-tetrad current Tetrad jar used in this project has been updated to the forthcoming Tetrad version 7.6.2.
* The pseudoinverse option was added to relevant tests and scores--see the TetradSearch.py class.
* An example file was added to show how to use the Markov checker

## SOME PLANS

* We are going to try to make Rpy-Tetrad to install.
    * The first step (soon) will be to make all paths _relative_ to the project path, which will be the py-tetrad directory.
    * It is also possible to automatically install the Java JDK from R locally. As soon as we can get this work on all platforms we will include that.

