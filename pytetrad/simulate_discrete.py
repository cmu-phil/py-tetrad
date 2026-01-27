## This script assumes that the user has pip-installed the pytetrad package. Here is now:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim
import edu.cmu.tetrad.algcomparison.graph as graph
import edu.cmu.tetrad.util as util
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.data as td
import java.util as ju

D, G = sim.simulateDiscrete(num_meas=100, samp_size=1000)

D = tr.tetrad_data_to_pandas(D)
G = tr.graph_to_matrix(G)

# Save data to a file
D.to_csv('../mydata.csv', index=False)
G.to_csv('../mygraph.csv', index=False)

tetrad_graph = graph.RandomForward().createGraph(util.Parameters())

D, G = sim.simulateDiscreteFromGraph(tetrad_graph)

print(G)
print(tr.tetrad_data_to_pandas(D))

x = td.DiscreteVariable("x", 3)
y = td.DiscreteVariable("y", 3)
z = td.DiscreteVariable("z", 3)
nodes = ju.ArrayList()
nodes.add(x)
nodes.add(y)
nodes.add(z)

tetrad_graph = tg.EdgeListGraph(nodes)
tetrad_graph.addDirectedEdge(x, y)
tetrad_graph.addDirectedEdge(y, z)

D, G = sim.simulateDiscreteFromGraph(tetrad_graph)

print(G)
print(tr.tetrad_data_to_pandas(D))