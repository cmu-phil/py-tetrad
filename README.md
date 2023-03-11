
# py-tetrad

This package shows how to make arbitrary code in [Tetrad](https://github.com/cmu-phil/tetrad) directly available in Python via [JPype](https://github.com/jpype-project/jpype) as part of a Python workflow. We do this by giving [reusable examples](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad) of how it can be done, along with [API Javadoc documentation](https://www.phil.cmu.edu/tetrad-javadocs/7.2.2/lib/) to allow further exploration of the entire Tetrad codebase.

Part of our code uses the [causal-learn Python package](https://github.com/py-why/causal-learn) to show how it can be integrated.
 
This replaces the older [py-causal](https://github.com/bd2kccd/py-causal) package.

You can also integrate Tetrad code into Python by making os.system (..) calls to [Causal Command](https://github.com/bd2kccd/causal-cmd); here are some [examples](https://github.com/cmu-phil/algocompy/blob/main/old/causalcmd/tetrad_cmd_algs.py) of how to do it.

This project is still new, so please bear with us as we add example modules and clarify the code. Please submit any problems to our [Issue Tracker](https://github.com/cmu-phil/py-tetrad/issues), and we'll see if we can solve them. Using JPype or Causal Command to integrate Tetrad code into a Python workflow is easy once you see how. Feel free to steal and modify code as needed.

We are also modifying some classes in Tetrad to make them easier to call from Python. We will maintain a [current version of the Tetrad launch jar](https://github.com/cmu-phil/py-tetrad/tree/main/pytetrad/resources), which is either the current published version or else the current published version with some [adjustments](https://github.com/cmu-phil/tetrad/wiki/Forthcoming-fixes). The example code will work with this current jar.

Our most recent stable Tetrad version, 7.2.2, is also included in the pytetrad/resources directory. But all artifacts for Tetrad for the last several releases are on [Maven Central](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/), along with signatures to verify their authenticity.

# Install

1. It is necessary to install a JAVA JRE or JDK, preferably the most recent version with long-term support (LTS), certainly greater than 1.8 (version 8). For stability across platforms, we find a [Corretto JRE/JDK Installation](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc) works well. 


1. If JAVA_HOME is not already set to the correct location of your Java installation above, you'll need to set it. On a Mac, you'd type in a terminal, `echo $JAVA_HOME` to see if it's set, and if not, type something like `export JAVA_HOME=/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk` to fix it. Adjust this for your platform and JDK/JRE installation path.

1. Make sure you are using the latest Python--at least 3.7--as required by JPype; if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

1. We use causal-learn, so all of its dependencies, and causal-learn itself, should be installed--see the [Docs for the causal-learn package](https://causal-learn.readthedocs.io/en/latest/).

1. We use the JPype package to interface Python with Java. For installation instructions, see the [Docs for the JPype box](https://jpype.readthedocs.io/en/latest/).

1. Finally, you will need to clone this GitHub repository, so if you don't have Git installed, google and install that for your machine type.

Then in a terminal window, for instance, cd to a directory where you want the cloned project to appear and type the following (or copy and paste it)--again, as above, make sure JAVA_HOME is set correctly to your java path):
    
```   
export JAVA_HOME=[path to your Java installation]
git clone https://github.com/cmu-phil/py-tetrad/
cd py-tetrad/pytetrad
python run_continuous.py
```

If everything is set up right, the last command should cause this example module to run various algorithms in (Java) Tetrad and print out result graphs. Feel free to explore other example modules in that directory.

Feel free to use your favorite method for editing and running modules.

**This is currently not stable; adjusting code. Also making some fixes to the Tetrad jar to help with some of the JPype issues we found--see the current jar.**
