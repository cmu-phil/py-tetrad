import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import graphviz as gviz

import tools.TetradSearch as search
import tools.translate as tr

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
