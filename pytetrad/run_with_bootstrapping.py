# This is an example of how to use the algcomparison API in Tetrad
# through JPype to do bootstrapping.

import jpype.imports

import os
import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), "-Xmx2g", classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

import pandas as pd

data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

import pytetrad.tools.TetradSearch as search

search = search.TetradSearch(data)
search.use_sem_bic(penalty_discount=2)
search.set_bootstrapping(numberResampling=10, percent_resample_size=100, with_replacement=True,
                         add_original=True, resampling_ensemble=1, seed=4130213)
search.run_fges()

print(search.get_java())
