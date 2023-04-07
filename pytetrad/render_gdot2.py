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

search.add_to_tier(0, "RIVER")
search.add_to_tier(0, "ERECTED")
search.add_to_tier(0, "PURPOSE")
search.add_to_tier(0, "LENGTH")
search.add_to_tier(0, "LANES")
search.add_to_tier(0, "CLEAR_G")
search.add_to_tier(0, "T_OR_D")
search.add_to_tier(0, "MATERIAL")
search.add_to_tier(0, "SPAN")
search.add_to_tier(0, "REL_L")
search.add_to_tier(1, "TYPE")

search.run_grasp()
g = search.get_java()

gdot = gviz.Graph(format='png', 
                  engine='dot', 
                  graph_attr={'viewport': '400', 
                              'outputorder': 'edgesfirst'})
tr.write_gdot(g, gdot)
gdot.render(filename="bridges", cleanup=True, quiet=True)
gdot.clear()

# print(search)
