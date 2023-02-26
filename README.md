# py-tetrad
Makes algorithms/code in (Java) Tetrad directly available in Python via [JPype](https://github.com/jpype-project/jpype).

Currently this package contains a translate.py file, which helps to translate datasets from Python (pandas) to Java (Tetrad) and graphs from Java (Tetrad) back into Python (two formats currently, the causal-learn graph format and the R PCALG format for general graphs). 

It also contains an examples.py file, which shows how to run several Tetrad searches on Python (pandas) data, for the continuous case and retrieve their result graphs back into Python.

We will shortly expand available data types to discrete and mixed continuous/discrete, and expand the example files, perhaps one for each of several algorithms, though of course the entire Tetrad codebase is made available via JPype. Also more graphs translation methods will be added, in both directions, so that more graph methods can be taken advantage of in Tetrad from Python.

JPype allows Java interfaces to be implemented in Python, which should make it possible to use Python scores and tests in the (Java) Tetrad code, from the point of view of Python, though this hasn't been done yet.
 
This already **replaces the older [py-causal](https://github.com/bd2kccd/py-causal) package for continuous datasets**, which used the buggy and hard-to-install Javabridge to connect Python to Java and used an outdated version of Tetrad, so please if you're using py-causal, watch this project and switch over as soon as it is stable. Also, if you're Python-based, consider using [causal-learn](https://github.com/py-why/causal-learn) algorithms where available.

# Install

1. We use causal-learn, so all of its dependencies, and causal-learn itself, should be installed--see the [Docs for the causal-learn package](https://causal-learn.readthedocs.io/en/latest/).

1. It is necessary to install a JAVA JRE or JDK, preferably the most recent version available with long term support (LTS), certainly greater than 1.8 (version 8). For stability across platforms, we find that a [Corretto JRE/JDK Installation](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc) works the best, 

    * It may be necessary, depending on how you set up your Python, to set JAVA_HOME to the path to this JRE/JDK installation.

1. We use the JPype package to interface Python with Java. For installation instructions, see the [Docs for the JPype package](https://jpype.readthedocs.io/en/latest/).

**This project is not yet stable.**
