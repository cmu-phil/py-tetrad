import jpype.imports

import os
import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), "-Xmx2g", classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim

D, G = sim.simulateDiscrete(num_meas=100, samp_size=1000)

D = tr.tetrad_data_to_pandas(D)
G = tr.graph_to_matrix(G)

# Save data to a file
D.to_csv('../mydata.csv', index=False)
G.to_csv('../mygraph.csv', index=False)
