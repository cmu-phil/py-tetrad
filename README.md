
# py-tetrad

This package shows how to make arbitrary code in [Tetrad](https://github.com/cmu-phil/tetrad) directly available in Python via [JPype](https://github.com/jpype-project/jpype) as part of a Python workflow. We do this by giving [reusable examples](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad) of how it can be done, along with [API Javadoc documentation](https://www.phil.cmu.edu/tetrad-javadocs/7.3.0/lib/) to allow further exploration of the entire Tetrad codebase.

Part of our code uses the [causal-learn Python package](https://github.com/py-why/causal-learn) to show how it can be integrated.

You can also integrate Tetrad code into Python by making os.system (..) calls to [Causal Command](https://github.com/bd2kccd/causal-cmd); here are some [examples](https://github.com/cmu-phil/algocompy/blob/main/old/causalcmd/tetrad_cmd_algs.py) of how to do it.

This project is still new, so please bear with us as we add example modules and keep our code up to date. Please submit any problems or suggestions to our [Issue Tracker](https://github.com/cmu-phil/py-tetrad/issues), so that we can solve them. In some cases it may not be obvious how to call a Tetrad class or method from Python; these issues need to be fixed in Tetrad. Please point out any difficulties you have, so that we can make it more intuitive to use.

We will maintain a [current version of the Tetrad launch jar](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/resources), which is either the current published version or else the current published version with some [adjustments](https://github.com/cmu-phil/tetrad/wiki/Forthcoming-fixes). The example code will work with this current jar. Feel free to use any version of Tetrad though. All artifacts for Tetrad for the last several releases are on [Maven Central](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/), along with their corresponding Javadocs and signatures to verify authenticity.

# Install

1. It is necessary to install a JAVA JRE or JDK, preferably the most recent version with long-term support (LTS), certainly greater than 1.8 (version 8). For stability across platforms, we find a [Corretto JRE/JDK Installation](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc) works well. 

1. If JAVA_HOME is not already set to the correct location of your Java installation above, you'll need to set it. On a Mac, you'd type in a terminal, `echo $JAVA_HOME` to see if it's set, and if not, type something like `export JAVA_HOME=/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk` to fix it. Adjust this for your platform and JDK/JRE installation path.

1. Make sure you are using the latest Python--at least 3.7--as required by JPype; if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

1. We use causal-learn. For installation instructions, see the [Docs for the causal-learn package](https://causal-learn.readthedocs.io/en/latest/).

1. We use the JPype package to interface Python with Java. For installation instructions, see the [Docs for the JPype box](https://jpype.readthedocs.io/en/latest/).

1. Finally, you will need to clone this GitHub repository, so if you don't have Git installed, google and install that for your machine type.

Then (for instance, on a Mac) in a terminal window, cd to a directory where you want the cloned project to appear and type the following--again, as above, make sure JAVA_HOME is set correctly to your java path):
    
```   
export JAVA_HOME=[path to your Java installation]
git clone https://github.com/cmu-phil/py-tetrad/
cd py-tetrad/pytetrad
python run_continuous.py
```

If everything is set up right, the last command should cause this example module to run various algorithms in Tetrad and print out result graphs. Feel free to explore other example modules in that directory.

Feel free to use your favorite method for editing and running modules.
