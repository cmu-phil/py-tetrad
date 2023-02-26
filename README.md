# py-tetrad
Makes algorithms/code in (Java) Tetrad available in Python via JPype

# Install

1. We use the causal-learn package, so all of its prerequiites should be installed:

    * https://github.com/py-why/causal-learn

1. We use the JPype package to interface Python with Java. For installation instructions, see the docs for that project:

    * https://jpype.readthedocs.io/en/latest/

1. It is necessary to install a JAVA JRE, preferably the most recent version available, certainly greater than 1.8 (version 8). For stability across platforms, we find that the  Corretto installation works the best, 

    * https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc

    * It may be necessary, depending on how you set up your Python, to set JAVA_HOME to your current python installation.

1. Finally, it is necessary to download the latest Tetrad launch jar from Maven Central. Here is the GitHub for Tetrad.

    * https://github.com/cmu-phil/tetrad

    * The latent jar is linked to from that ReadMe.md file on that site (scroll down). The current javadocs for this version are also available, if one wishes to download these from the Maven Central site.

Currently the Java JRE and Tetrad jar links are hard-coded in relevant py files and will need to be set by the user; we will try to figure out a way to make those links automatic.
