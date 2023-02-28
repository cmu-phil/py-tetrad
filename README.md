# py-tetrad
This package makes algorithms/code in (Java) Tetrad directly available in Python via [JPype](https://github.com/jpype-project/jpype).

Currently the package contains a translate.py file, which helps to translate datasets from Python (pandas) to Java (Tetrad) and graphs from Java (Tetrad) back into Python (two formats currently, the causal-learn graph format and the R PCALG format for general graphs). 

It also contains an examples_continuous.py file, and examples_discrete.py file, and an examples_mixed.py file, which show how to run several Tetrad searches on Python (pandas) data, for the continuous case, discrete and mixed continuous/discrete cases and retrieve their result graphs back into Python.

We will shortly expand the example files, showing how to run a variety of different types of searches through JPypa in Tetrad. (Of course the entire Tetrad codebase is made available via JPype, so more is possible.) Also more graphs translation methods will be added, in both directions, so that more graph methods can be taken advantage of in Tetrad from Python. For instance, the GeneralGraph class in causal-learn is being migrated to a new format; we will add translators for that soon.

JPype allows Java interfaces to be implemented in Python, which should make it possible to use causal-learn scores and tests in the (Java) Tetrad code, from the vantage point of Python, though this hasn't been done yet.

We will add Read The Docs documentation.
 
This **replaces the older [py-causal](https://github.com/bd2kccd/py-causal) package**, which used Javabridge to connect Python to Java, with an outdated version of Tetrad, so please if you're using py-causal, watch this project and switch over as soon as it is stable. **We may optionally put this code into the py-causal module as a new version.** 

If you're Python-based, you could consider using [causal-learn](https://github.com/py-why/causal-learn) algorithms where available.

# Install

1. It is necessary to install a JAVA JRE or JDK, preferably the most recent version available with long term support (LTS), certainly greater than 1.8 (version 8). For stability across platforms, we find that a [Corretto JRE/JDK Installation](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc) works well.

    * It may be necessary, depending on how you set up your Python, to set JAVA_HOME to the path to this JRE/JDK installation.

1. Make sure you are using the latest Python--at least 3.7--as required by JPype; if not, [update it](https://www.pythoncentral.io/how-to-update-python/). The version of Python needs to be at least 3.7, since JPype requires all of underlying references to Python 2 be eliminated--see the [JPype documentation](https://jpype.readthedocs.io/en/latest/).

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

**This project is not yet stable--it will be expanded in ways listed above, though the example files are correct. Also, this may possibly be moved into the py-causal module as a new version.**
