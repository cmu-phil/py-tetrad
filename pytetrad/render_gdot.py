import jpype.imports

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

import pandas as pd
import graphviz as gviz

import pytetrad.tools.TetradSearch as search
import pytetrad.tools.translate as tr

data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

search = search.TetradSearch(data)
search.set_verbose(False)

search.use_sem_bic(penalty_discount=1)
search.use_fisher_z(alpha=0.05)

search.run_spfci()
g = search.get_java()

gdot = gviz.Graph(format='png', 
                  engine='dot', 
                  graph_attr={'viewport': '400', 
                              'outputorder': 'edgesfirst'})
tr.write_gdot(g, gdot)
gdot.render(filename="airfoil_graph", cleanup=True, quiet=True)
gdot.clear()
