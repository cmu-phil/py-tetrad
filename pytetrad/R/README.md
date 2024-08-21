## RPy-Tetrad: Py-Tetrad for R and RStudio

This project is being offered as a way of connecting Tetrad to R through Python. It is intended to replace the older (less maintainable) [r-causal](https://github.com/bd2kccd/r-causal) Python project that uses an outdated version of Tetrad.

Here are [INSTALLATION INSTRUCTIONS](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/INSTALLATION.md).

Here is some [INITIAL DOCUMENTATION](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/DOCUMENTATION.md).

If you have questions or need more (or different) functionality, or are just flummoxed by the installation procedure, available algorihtms, knowledge functionality, or output graph formats, [let us know](https://github.com/cmu-phil/py-tetrad/issues). Although all of the functionality is from an established project, [Tetrad](https://github.com/cmu-phil/tetrad), this R interface has been available only as of 2023-04-04, so [feedback](https://github.com/cmu-phil/py-tetrad/issues) is very welcome. And thanks for all the feedback we've gotten so far--much appreciated!

## NEWS

* Rpy-tetrad paths for the sample files are all made relative to the directory .../py-tetrad/pytetrad. In RStudio, the idea is to load .../py-tetrad/pytetrad as the project and run the scripts from there.
* A setup.py file has been included to download a JDK locally and set up a Python virtual environment locally. THIS HAS ONLY BEEN TESTED ON ONE MAC LAPTOP SO USE AT YOUR OWN RISK. The previous setup should work if you do not run the setup.py script. If you try the setup.py script and things go badly, quit RStudio and restart.
* Sample script #11 runs BOSS using _rJava_, which avoids using Python. THIS IS NOT FULLY TESTED. If this works out well, we may try to revive the r-causal package, but with the updated rJava, by implementing a TetradSearch.R script in R that's parallel to the TetradSearch.py script in rpy-tetrad.

