
# py-tetrad

This package shows how to make arbitrary code in [Tetrad](https://github.com/cmu-phil/tetrad) directly available in Python via [JPype](https://github.com/jpype-project/jpype) as part of a Python workflow. We do this by giving [reusable examples](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad) of how it can be done, along with [API Javadoc documentation](https://www.phil.cmu.edu/tetrad-javadocs/7.3.4/lib/) to allow further exploration of the entire Tetrad codebase.

Part of our code uses the [causal-learn Python package](https://github.com/py-why/causal-learn) in [py-why](https://github.com/py-why) to show how it can be integrated.

You can also integrate Tetrad code into Python by making os.system (..) calls to [Causal Command](https://github.com/bd2kccd/causal-cmd); here are [some examples](https://github.com/cmu-phil/algocompy/blob/main/old/causalcmd/tetrad_cmd_algs.py) of how to do it.

Please bear with us as we add and refine example modules and keep our code up to date. Please submit any problems or suggestions to our [Issue Tracker](https://github.com/cmu-phil/py-tetrad/issues), so that we can resolve them. In some cases it may not be obvious how to call a Tetrad class or method from Python. Please point out any difficulties you have, so that we can make it more intuitive to use for the next version.

We maintain a [current version of the Tetrad launch jar](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/resources), which is either the [current published version](https://github.com/cmu-phil/tetrad/releases) or else the current published version with some [adjustments](https://github.com/cmu-phil/tetrad/wiki/Forthcoming-fixes). The example code will work with this current jar. Feel free to use any version of Tetrad though. All artifacts for Tetrad for the last several releases are on [Maven Central](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/), with their corresponding API Javadocs, along wth signatures to verify authenticity.

We added [a method to use Tetrad algorithms in R via py-tetrad](https://github.com/cmu-phil/py-tetrad/blob/main/pytetrad/R/). This is work in progress.

# Install

1. It is necessary to install a JDK. For this, see our Wiki article, [Setting up Java for Tetrad](https://github.com/cmu-phil/tetrad/wiki/Setting-up-Java-for-Tetrad).

1. If JAVA_HOME is not already set to the correct location of your Java installation above, you'll need to [set JAVA_HOME](https://www.baeldung.com/java-home-on-windows-7-8-10-mac-os-x-linux#:~:text=On%20the%20Desktop%2C%20right%2Dclick,Variable%20value%20and%20click%20OK.) to the path of the Java installation you want to use for py-tetrad.

1. Make sure you are using the latest Python--at least 3.7--as required by JPype; if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

1. We use causal-learn. For installation instructions, see the [Docs for the causal-learn package](https://causal-learn.readthedocs.io/en/latest/).

1. We use the JPype package to interface Python with Java. For installation instructions, see the [Docs for the JPype box](https://jpype.readthedocs.io/en/latest/).

1. Finally, you will need to clone this GitHub repository, so if you don't have Git installed, google and install that for your machine type.

Then (for instance, on a Mac) in a terminal window, cd to a directory where you want the cloned project to appear and type the following--again, as above, make sure JAVA_HOME is set correctly to your java path:
    
```   
git clone https://github.com/cmu-phil/py-tetrad/
cd py-tetrad/pytetrad
python run_continuous.py
```

If everything is set up right, the last command should cause this example module to run various algorithms in Tetrad and print out result graphs. Feel free to explore other example modules in that directory.

Feel free to use your favorite method for editing and running modules.

# Citation

Please cite as: 

Bryan Andrews and Joseph Ramsey. https://github.com/cmu-phil/py-tetrad, 2023.
