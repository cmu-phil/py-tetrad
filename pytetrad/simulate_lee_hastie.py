import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import tools.translate as tr
import tools.simulate as sim

## Simulates data with both continuous and discrete columns.
D, G = sim.simulateLeeHastie(num_meas=100, samp_size=1000)

D = tr.tetrad_to_pandas(D)
G = tr.tetrad_graph_to_causal_learn(G)

# Save data to a file
D.to_csv('../mydata.csv', index=False)

# To save out causal learn graph:
with open('../mygraph.txt', 'w') as f:
    f.write(str(G))
