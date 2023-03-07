import os
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

import jpype
import jpype.imports

# this needs to happen before import pytetrad (otherwise lib cant be found)
try:
    jpype.startJVM(classpath=[f"{BASE_DIR}/tetrad-gui-7.2.2-launch.jar"])
except OSError:
    print("JVM already started")

import pytetrad.simulate as util

# D, G = util.simulateContinuous(num_meas=100, samp_size=1000)
D, G = util.simulateContinuous(num_meas=5, avg_deg=2, samp_size=600)

# Save data to a file
D.to_csv('../mydata.csv', index=False)

# To save out causal learn graph:
with open('../mygraph.txt', 'w') as f:
    f.write(str(G))
