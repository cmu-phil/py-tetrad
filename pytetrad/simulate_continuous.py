import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim

D, G = sim.simulateContinuous(num_meas=100, samp_size=1000)

D2 = tr.tetrad_data_to_pandas(D)
G2 = tr.graph_to_matrix(G)

# Save data to a file
D2.to_csv('../mydata.csv', index=False)
G2.to_csv('../mygraph.csv', index=False)
