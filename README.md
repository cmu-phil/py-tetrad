# py-tetrad
This package shows how to make algorithms/code in [Tetrad](https://github.com/cmu-phil/tetrad) directly available in Python via [JPype](https://github.com/jpype-project/jpype). One is not of course limited to doing it this way; we aim mainly to be giving examples of how it can be done along with some methods for translating dataset, graphs, and such, between Java and Python to make it easier to use Tetrad as part of a Python workflow.

Part of our translations an examples make use of the [causal-learn](https://github.com/py-why/causal-learn) Python pacakge for causal structure learning.
 
This is intended to replace the older [py-causal](https://github.com/bd2kccd/py-causal) package, which used Javabridge to connect Python to Java. Javabridge was difficult to install (and buggy) on some platforms and used an outdated version of Tetrad, so if you're using py-causal, watch this project and switch over as soon as it is stable. We may optionally put this code into the py-causal module as a new version. Once nice thing about In py-causal was that there were many worked examples; we will aim to provide an adequate set of examples for py-tetrad as well. Also, in some cases it's difficult o know how to use the Tetrad API; we will aim to clean up the Tetrad API for these cases for the _next_ version of Tetrad, 7.3.9.

We're currently using the stable Tetrad version 7.2.2, which is hard-coded for use in the project. All artifacts for Tetrad (including javadocs) are on [Maven Central](https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/). If you'd like to view the javadocs, download them into a new directory and unzip them; then view the in a browser.

# Install

1. It is necessary to install a JAVA JRE or JDK, preferably the most recent version available with long term support (LTS), certainly greater than 1.8 (version 8). For stability across platforms, we find that a [Corretto JRE/JDK Installation](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc) works well.

    * It may be necessary, depending on how you set up your Python, to set JAVA_HOME to the path to this JRE/JDK installation.

1. Make sure you are using the latest Python--at least 3.7--as required by JPype; if not, [update it](https://www.pythoncentral.io/how-to-update-python/). 

1. We use causal-learn, so all of its dependencies, and causal-learn itself, should be installed--see the [Docs for the causal-learn package](https://causal-learn.readthedocs.io/en/latest/).

1. We use the JPype package to interface Python with Java. For installation instructions, see the [Docs for the JPype package](https://jpype.readthedocs.io/en/latest/).

1. Finally, you will need to clone this GitHub repository, so if you don't have Git installed, first google and install that for your machine type, and then in a terminal window cd to a directory where you want the cloned project to appear and type (on a Mac--make adjustments for other platforms and adjusting the JAVA_HOME path to your version of the JRE/JDK):

      git clone https://github.com/cmu-phil/py-tetrad
      
      cd py-tetrad/examples
      
      export JAVA_HOME=/Library/java/JavaVirtualMachines/amazon-corretto-18.jdk
      
      python3 examples_continuous.py
      
      python3 examples_discrete.py
    
      python3 examples_mixed.py

These last three commands should cause the examples to run various algorithms in (Java) Tetrad and print out result graphs in several different ways in Python--using the original Java graph class, using the PCALG-style general graph matrix, and using GeneralGraph in causal-learn.

You can of course load py-causal into a Python editor like PyCharm. The only issue at the moment is that PyCharm does not recognize the Java packages and puts some read underlining in the editor that you can't get rid of. Just ignore such red underlining for Java packages; the modules will run.

**This project is not yet stable--it will be expanded in ways listed above, though the example files are correct. Also, this may possibly be moved into the py-causal module as a new version.**
