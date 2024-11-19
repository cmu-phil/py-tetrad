# py-tetrad

Please visit our [Tetrad web page](https://www.cmu.edu/dietrich/philosophy/tetrad/) for current links for downloadables, a list of contributors, some history, documentation, descriptions, links for our various projects, Javadocs, and more.

This package shows how to make arbitrary code in [Tetrad](https://github.com/cmu-phil/tetrad) directly available in Python via [JPype](https://github.com/jpype-project/jpype) as part of a Python workflow. We do this by giving some [tools](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/tools) for translating graphs and datasets from Python to Java and back, providing some [reusable examples](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad) of how it can be done, and giving [API Javadoc documentation](https://www.phil.cmu.edu/tetrad-javadocs/7.6.5/) to allow further exploration of the entire Tetrad codebase.

It also provides a class, [TetradSearch.py](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/tools/TetradSearch.py), that can be used in both Python and R to hide the JPype facilities for those who don't want to (or can't, in the case of R) deal directly with the Tetrad codebase.

You can also integrate Tetrad code into Python by making os.system (..) calls to [Causal Command](https://github.com/bd2kccd/causal-cmd); here are [some examples](https://github.com/cmu-phil/algocompy/blob/main/old/causalcmd/tetrad_cmd_algs.py) of how to do it. For R functionality, see [rpy-tetrad](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/), which is located in a subdirectory of the py-tetrad project in GitHub.

Please bear with us as we add and refine example modules and keep our code current. Please submit any problems or suggestions to our [Issue Tracker](https://github.com/cmu-phil/py-tetrad/issues), so that we can resolve them. Sometimes it may not be obvious how to call a Tetrad class or method from Python. Please point out any difficulties you have, so we can make it more intuitive for the next version.

We maintain a [current version of the Tetrad launch jar](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/resources), which is either the [current published version](https://github.com/cmu-phil/tetrad/releases) or else the current published version with some [adjustments](https://github.com/cmu-phil/tetrad/wiki/Forthcoming-fixes). We will make sure that the example code will work with this current jar. Feel free to use any version of Tetrad, though. All artifacts for Tetrad for the last several releases are on [Maven Central](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/), with their corresponding API Javadocs, along wth signatures to verify authenticity.

We should clarify that once you see how to use JPype to run Tetrad code in Python, you do not need this repository to do that. All you need is the Tetrad documentation (which we will try to keep up to date) and a little advice here or there, which we are happy to provide. Also, you may want to copy the [data and translation methods](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/tools) from this repository into your own code--feel free to steal those and modify them to your own purposes. This repository, from the point of view of Python, is a ladder really that, once you've climbed a little, you can toss away. From R, using [rpy-tetrad](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/), it's a different story; we can't figure out how to use JPype directly in R, so this repository helps.

# News

2024-11-18

- Added a pip install option and converted examples files to use it where feasible.

# Install

1. A JDK installed for version 21+ is necessary. See our Wiki article, [Setting up Java for Tetrad](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

1. type ``echo $JAVA_HOME``in a terminal to see if this is already set to your JDK. On Windows, it should already be set if you've installed Java. On Mac, it should be set to the latest JDK installed. If it's not set, you'll need to [set JAVA_HOME](https://www.baeldung.com/java-home-on-windows-7-8-10-mac-os-x-linux#:~:text=On%20the%20Desktop%2C%20right%2Dclick,Variable%20value%20and%20click%20OK.) to the path of the Java installation you want to use for py-tetrad.

1. Confirm you have a Python version of agt least 3.5. Here is how to [update Python](https://www.pythoncentral.io/how-to-update-python/) if you need to.

1. Install JPype via pip:

   ```
   pip install JPype1
   ```

1. Install py-tetrad via pip:

   ```
   pip install git+https://github.com/cmu-phil/py-tetrad
   ```

3. Clone the repository and run an example file:

   ```
   git clone https://github.com/cmu-phil/py-tetrad/
   cd py-tetrad/pytetrad
   python run_continuous.py
   ```

If everything is set up right, this should cause this example module to run various algorithms in Tetrad and print out result graphs. Feel free to explore other example modules in that directory.

Feel free to use your favorite method for editing and running modules.

# Citation

Please cite as: 

Ramsey, J., & Andrews, B. (2023, November). Py-Tetrad and RPy-Tetrad: A New Python Interface with R Support for Tetrad Causal Search. In Causal Analysis Workshop Series (pp. 40-51). PMLR.
