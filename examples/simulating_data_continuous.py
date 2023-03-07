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

import pytetrad.translate as tr
import pytetrad.util as util

D, G = util.simulateContiuous(num_meas=100, samp_size=1000)

#Save data to a file
df = tr.tetrad_to_pandas(D)
df.to_csv('../mydata.csv', index=False)

# To save out causal learn graph:
G_ = tr.tetrad_graph_to_causal_learn(G)
with open('../mygraph.txt', 'w') as f:
    f.write(str(G_))

# To save out in PCALG format:
G_ = tr.tetrad_graph_to_pcalg(G)
G_.to_csv('../mygraph.csv', index=False)



