# py-tetrad

This package shows how to make algorithms/code in [Tetrad](https://github.com/cmu-phil/tetrad) directly available in Python via [JPype](https://github.com/jpype-project/jpype) as part of a Python workflow.

Part of our code makes use of the [causal-learn](https://github.com/py-why/causal-learn) Python package for causal structure learning, to show how it can be integrated with that.
 
This is intended to replace the older [py-causal](https://github.com/bd2kccd/py-causal) package.

You can also integrate Tetrad code into Python by making os.system(..) calls to [Causal Command](https://github.com/bd2kccd/causal-cmd); here are some [examples](https://github.com/cmu-phil/algocompy/blob/main/old/causalcmd/tetrad_cmd_algs.py) of how to do it.

This is still a new project, so please bear with us as we add example modules and clarify the code. Please submit any problems you have figuring things out to our [Issue Tracker](https://github.com/cmu-phil/py-tetrad/issues) and we'll see if we can solve them. Actually, using JPype or Causal Command to integrate Tetrad code into a Python workflow is pretty easy once you see how to do it. This is not a complicated project; feel free to steal code as needed.

In fact, the main problem for calling arbitrary code from Tetrad using JPype is figuring out what classes are available and what methods to call and what their signatures are; we'll try to make that easier. It helps to consult the javadocs for Tetrad. If you'd like to view the javadocs for Tetrad 7.2.2, click [here](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/tetrad-lib/7.2.2/) to download them, then move them into a _new directory_ and unzip them; then view them in a browser. Hopefully, though, we can just add or clarify examples for the main things you may want to do.

Another problem is that some code in Tetrad is not written in a way to make it easy to call from Python; where we find issues like this in our examples, we will try for the next version of Tetrad to clean that up.

We're currently using the most recent stable Tetrad version 7.2.2, which is included in the project--all of the examples in the project are using this versioin. But all artifacts for Tetrad for the last several releases are on [Maven Central](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/), along with signatures to verify their authenticity.

# Install

1. It is necessary to install a JAVA JRE or JDK, preferably the most recent version available with long term support (LTS), certainly greater than 1.8 (version 8). For stability across platforms, we find that a [Corretto JRE/JDK Installation](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc) works well. 


1. If JAVA_HOME is not already set to the correct location of your Java installation above, you'll need to set it--on a Mac you'd type in a terminal, "echo $JAVA_HOME" to see if it's set, and if not, type something like something like, "export JAVA_HOME=/opt/anaconda3", to set it. Adjust this for your platform and JDK/JRE installation path.

1. Make sure you are using the latest Python--at least 3.7--as required by JPype; if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

1. We use causal-learn, so all of its dependencies, and causal-learn itself, should be installed--see the [Docs for the causal-learn package](https://causal-learn.readthedocs.io/en/latest/).

1. We use the JPype package to interface Python with Java. For installation instructions, see the [Docs for the JPype package](https://jpype.readthedocs.io/en/latest/).

1. Finally, you will need to clone this GitHub repository, so if you don't have Git installed, google and install that for your machine type.

Then in a terminal window,for instance, cd to a directory where you want the cloned project to appear and type the following (or just copy and paste it--again, as above, make sure JAVA_HOME is set correctly in the below to your java path):
    
```   
export JAVA_HOME=[path to your Java installation]
git clone https://github.com/cmu-phil/py-tetrad/
pip install ./py-tetrad 
cd py-tetrad/examples
python run_searches_on_continuous_data.py
```

If everything is set up right, the last command should cause this example module to run various algorithms in (Java) Tetrad and print out result graphs in several different ways in Python--using the original Java graph class, using the PCALG-style general graph matrix, and using GeneralGraph in causal-learn. Feel free to explore other example modules in that directory.

**This is currently not stable; adjusting code**
