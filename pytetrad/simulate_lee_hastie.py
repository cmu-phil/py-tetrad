import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import tools.translate as tr
import tools.simulate as sim

## Simulates data with both continuous and discrete columns.
D, G = sim.simulateLeeHastie(num_meas=100, samp_size=1000)

D = tr.tetrad_data_to_pandas(D)
G = tr.tetrad_graph_to_pcalg(G)

# Save data to a file
D.to_csv('../mydata.csv', index=False)
G.to_csv('../mygraph.csv', index=False)
