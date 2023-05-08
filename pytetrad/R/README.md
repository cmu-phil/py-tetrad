## RPy-Tetrad: Py-Tetrad for R and RStudio

This project is being offered as a possible way of connecting Tetrad to R which we are developimg. It is intended to replace the older [r-causal](https://github.com/bd2kccd/r-causal) Python project that uses an outdated version of Tetrad.

Here are [INSTALLATION INSTRUCTIONS](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/INSTALLATION.md).

Here is some [INITIAL DOCUMENTATION](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/DOCUMENTATION.md).

If you have questions or need more (or different) functionality, or are just flummoxed by the installation procedure, available algorihtms, knowledge functionality, or output graph formats, [let us know](https://github.com/cmu-phil/py-tetrad/issues). Although all of the functionality is from an established project, [Tetrad](https://github.com/cmu-phil/tetrad), this R interface is new as of 2023-04-04, so [feedback](https://github.com/cmu-phil/py-tetrad/issues) is very welcome. We'd like to make this useful for the R community and will put some effort into making that happen.

NEWS:

* 2023-4-5: Initial beta release
* 2023-4-11: The Tetrad bootstrapping facility was added to TetradSearch.py, and all algorithm, search, and test parameters for the algorithms, searches, and tests available in this module are now available as arguments to those methods.
* 2023-4-13: In Tetrad, the class name convention was enforced to make sure they start with capitqal letters and are camel case after that; this required some adjustments to the RPyTetrad code. Switched to recommending the DiagrammeR package instead of DiagrammR; this seems to be supported on more recent versions of R.
* 2023-4-14: Removed search.py and replaces uses of it in the examples and R scripts with TetradSearch.py.
