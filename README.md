# py-tetrad

This package shows how to make algorithms/code in [Tetrad](https://github.com/cmu-phil/tetrad) directly available in Python via [JPype](https://github.com/jpype-project/jpype).

Part of our code makes use of the [causal-learn](https://github.com/py-why/causal-learn) Python pacakge for causal structure learning, to show how it can be integrated with that.
 
This is intended to replace the older [py-causal](https://github.com/bd2kccd/py-causal) package. The installation procedure is much easier cross-platform, and the most recent Tetrad can be used. One nice thing about py-causal was that there were many worked examples; we will aim to provide an adequate set of examples for py-tetrad as well. Also, in some cases it's difficult to know how to use the Tetrad API; we will aim to clean up the Tetrad API for these cases for the next version of Tetrad. Please add issues to our [Issue Tracker](https://github.com/cmu-phil/py-tetrad/issues) if you have problems, so we can work to make things easier, especially as this is still a new project.

We're currently using the stable Tetrad version 7.2.2, which is hard-coded for use in the project. All artifacts for Tetrad are on [Maven Central](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/). If you'd like to view the javadocs for Tetrad 7.2.2, click [here](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/tetrad-lib/7.2.2/tetrad-lib-7.2.2-javadoc.jar) to download them, then move them into a new directory and unzip them; then view them in a browser.

The [JPype project](https://github.com/jpype-project/jpype) is already quite awesome, and one is not of course limited to integrating Tetrad into Python using JPype as is done in py-tetrad. We aim mainly to be giving examples of _how_ it can be done along with some methods for translating datasets, graphs, and such, between Java and Python to make it easier to use Tetrad as part of a Python workflow. Feel free to borrow as needed.

# Install

1. It is necessary to install a JAVA JRE or JDK, preferably the most recent version available with long term support (LTS), certainly greater than 1.8 (version 8). For stability across platforms, we find that a [Corretto JRE/JDK Installation](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc) works well. 


1. If JAVA_HOME is not already set to the correct location of your Java installation above, you'll need to set it--on a Mac you'd type in a terminal, "echo $JAVA_HOME" to see if it's set type something like something like, "export JAVA_HOME=/Library/java/JavaVirtualMachines/amazon-corretto-18.jdk", to set it. Adjust this for your platform and JDK/JRE installation path.

1. Make sure you are using the latest Python--at least 3.7--as required by JPype; if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

1. We use causal-learn, so all of its dependencies, and causal-learn itself, should be installed--see the [Docs for the causal-learn package](https://causal-learn.readthedocs.io/en/latest/).

1. We use the JPype package to interface Python with Java. For installation instructions, see the [Docs for the JPype package](https://jpype.readthedocs.io/en/latest/).

1. Finally, you will need to clone this GitHub repository, so if you don't have Git installed, google and install that for your machine type.

Then in a terminal window,for instance, cd to a directory where you want the cloned project to appear and type the following (or just copy and paste it):
    
```      
git clone https://github.com/cmu-phil/py-tetrad
cd py-tetrad/examples
python3 run_searches_on_continuous_data.py
```

If everything is set up right, the last command should cause this example module to run various algorithms in (Java) Tetrad and print out result graphs in several different ways in Python--using the original Java graph class, using the PCALG-style general graph matrix, and using GeneralGraph in causal-learn. Feel free to explore other example modules in that directory.

You can of course use your favorite method for editing and running Python modules. One caveat--if you load py-causal in PyCharm, an issue is that PyCharm does not recognize the Java packages and puts some red underlining in the editor that you can't get rid of. Just ignore such red underlining for Java packages; the modules will run. 
