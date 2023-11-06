import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import tools.translate as tr
import tools.simulate as sim

D, G = sim.simulateDiscrete(num_meas=100, samp_size=1000)

D = tr.tetrad_data_to_pandas(D)
G = tr.graph_to_matrix(G)

# Save data to a file
D.to_csv('../mydata.csv', index=False)
G.to_csv('../mygraph.csv', index=False)
