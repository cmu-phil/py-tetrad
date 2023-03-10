import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import tools.simulate as util

D, G = util.simulateContinuous(num_meas=100, samp_size=1000)
# D, G = util.simulateContinuous(num_meas=5, avg_deg=2, samp_size=600)

# Save data to a file
D.to_csv('../mydata.csv', index=False)

# To save out causal learn graph:
with open('../mygraph.txt', 'w') as f:
    f.write(str(G))
