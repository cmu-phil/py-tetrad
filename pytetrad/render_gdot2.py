import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd
import graphviz as gviz

import tools.TetradSearch as search
import tools.translate as tr

data = pd.read_csv("resources/bridges.data.version211_rev.txt", sep="\t")
# data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
# data = data.astype({col: "float64" for col in data.columns})

search = search.TetradSearch(data)
search.set_verbose(False)

search.use_bdeu()
search.use_chi_square()

search.add_to_tier(1, "RIVER")
search.add_to_tier(1, "ERECTED")
search.add_to_tier(1, "PURPOSE")
search.add_to_tier(1, "LENGTH")
search.add_to_tier(1, "LANES")
search.add_to_tier(1, "CLEAR.G")
search.add_to_tier(1, "T.OR.D")
search.add_to_tier(1, "MATERIAL")
search.add_to_tier(1, "SPAN")
search.add_to_tier(1, "REL.L")
search.add_to_tier(2, "TYPE")

search.run_grasp()
g = search.get_java()

gdot = gviz.Graph(format='png', 
                  engine='dot', 
                  graph_attr={'viewport': '400', 
                              'outputorder': 'edgesfirst'})
tr.write_gdot(g, gdot)
gdot.render(filename="airfoil_graph", cleanup=True, quiet=True)
gdot.clear()
