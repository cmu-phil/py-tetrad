import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import edu.cmu.tetrad.graph as tgraph
import edu.cmu.tetrad.search.utils as tsu
import java.io as io

# Load the text graph I made earlier with a selection and a latent in it.
# Print the graph to console.
# Run DAG to PAG to get the PAG. (This is still not right I don't think.)
# Print the PAG

graph = tgraph.GraphSaveLoadUtils.loadGraphTxt(io.File("resources/graph_with_selection.txt"))
print(graph)
pag = tsu.DagToPag(graph).convert()
print(pag)
