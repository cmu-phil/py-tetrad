# Some Initial Documentation

Click here for [Installation Instructions](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/INSTALLATION.md).

This section will eventualy turn into some bonafide documentation; please be patient. For information on specific algorithms, tests, or scores, or if you'd like to watch some videos on causal search, please see the [Documentation Section on the Tetrad GitHub page](https://github.com/cmu-phil/tetrad#documentation). if you are familiar with Tetrad, these are the same algorithms, tests, and scores that are available in the Search box in the current Tetrad interface, and in the current py-tetrad, and will work exactly the same way.

These algorithms currently output graphs in the PCALG general graph format, as R data frames. These are square edge matrices, see the docs for FCI in the PCALG package:

* 0 means NO endpoint
* 1 means CIRCLE endpoint (-o)
* 2 means ARROW endpoint (->)
* 3 means TAIL endpoint (--)

So for X-->Y, the output matrix G, where the index of X is i and the index of Y is j, would have G[j][i] = 3 and G[i][j] = 2.

Feel free to select a different algorithm or a different test or score in the script or choose a different, or write your own. We will assume for now that you're just run this script from the installation instructions: 'py-tetrad/pytetrad/R/sample_r_code2.R'. On a Mac, after you've run the script once, look at the line in the script where it says:

g = ts$run_fges()

Here, position your mouse to right right of the '$' sign and on the keyboard type control-Space. This will bring up a list of algorithms you can run, and you can select a different algorithm if you like. 

Similarly for tests or scores; you can select different tests or scores using the same method. There are some considerations. Some algorithms use just a score, like FGES; others use just a test, like PC; others still use both a test and a score, like GFCI. If you provide the wrong options, it will tell you.

Also, which test or score you choose will depend on the type of data you have. We give examples files 'sample_r_code2.R', 'sample_r_code3.R', and 'sample_r_code4.R', which show how to run a search on continuous, discrete, and mixed continuous/discrete data, respectively. If you choose badly, it will tell you.

As shown in the script, you can set background knowledge as indicated. Knowledge is organized into temporal tiers, where variables in later tiers cannot cause variables in earlier tiers, though explicit forbidden or required edges can also be set. Some algorithms do not use knowledge, but no worries, if you provide knowledge and the algorithm can't use it, it will tell you.


