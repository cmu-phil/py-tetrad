# py-tetrad
Makes algorithms/code in (Java) Tetrad available in Python via JPype.

Currently this package contains a translate.py file, which helps to translate datasets from Python (pandas) to Java (Tetrad) and graphs from Java (Tetrad) back into Python (two formats so far). 

It also contains an examples.py file, which shows how to run Tetrad searches on Python (pandas) data, for the continuous case. 

We will shortly expand available data types to discrete and mixed continuous/discrete, and expand the example files, perhaps one for each of several algorithms. Also more graphs translation methods will be added, in both diredctions, so that more graph methods can be taken advantage of in Tetrad from Python.
 
This already replaces the older [py-causal](https://github.com/bd2kccd/py-causal) package for continuous datasets, which used the buggy and hard-to-install Javabridge to connect Python to Java and used an outdated version of Tetrad.

# Install

1. We use the causal-learn package, so all of its prerequiites should be installed:

    * https://github.com/py-why/causal-learn

1. We use the JPype package to interface Python with Java. For installation instructions, see the docs for that project:

    * https://jpype.readthedocs.io/en/latest/

1. It is necessary to install a JAVA JRE, preferably the most recent version available, certainly greater than 1.8 (version 8). For stability across platforms, we find that the  Corretto installation works the best, 

    * https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc

    * It may be necessary, depending on how you set up your Python, to set JAVA_HOME to your current python installation.
