import causallearn
import numpy as np

import jpype.imports
from jpype.types import *

import os

from causallearn.graph.GeneralGraph import GeneralGraph
from causallearn.graph.GraphNode import GraphNode
from causallearn.graph.Endpoint import Endpoint
from causallearn.graph.Edge import Edge


# os.system('echo export "JAVA_HOME=\\$(/usr/libexec/java_home)" >> ~/.zshrc')
# jpype.startJVM(classpath=["/Users/bryanandrews/Desktop/tetrad-gui-7.2.2-launch.jar"])
os.environ["JAVA_HOME"] = "/usr/libexec/java_home"
jpype.startJVM(classpath=["/Users/josephramsey/Downloads/tetrad-gui-7.2.2-launch.jar"])

import java.util as util

import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg


def data_frame_to_tetrad_data(df):
    cols = df.columns
    values = df.values
    n, p = df.shape

    databox = td.DoubleDataBox(n, p)
    variables = util.ArrayList()
    for col, var in enumerate(values.T):
        variables.add(td.ContinuousVariable(cols[col]))
        for row, val in enumerate(var):
            databox.set(row, col, val)

    return td.BoxDataSet(databox, variables)


def tetrad_graph_to_pcalg(g):
    mark2Int = util.HashMap()
    mark2Int.put(tg.Endpoint.NULL, 0)
    mark2Int.put(tg.Endpoint.CIRCLE, 1)
    mark2Int.put(tg.Endpoint.ARROW, 2)
    mark2Int.put(tg.Endpoint.TAIL, 3)

    n = JInt(g.getNumNodes())
    A = np.zeros((n, n), dtype=int)
    nodes = g.getNodes()

    for edge in g.getEdges():
        i = nodes.indexOf(edge.getNode1())
        j = nodes.indexOf(edge.getNode2())
        A[j][i] = mark2Int.get(edge.getEndpoint1())
        A[i][j] = mark2Int.get(edge.getEndpoint2())

    return A


def tetrad_graph_to_causal_learn(g):
    endpoint_map = {"TAIL": Endpoint.TAIL,
                    "NULL": Endpoint.NULL,
                    "ARROW": Endpoint.ARROW,
                    "CIRCLE": Endpoint.CIRCLE,
                    "STAR": Endpoint.STAR}

    nodes = [GraphNode(str(node.getName())) for node in g.getNodes()]
    graph = causallearn.graph.GeneralGraph.GeneralGraph(nodes)

    for edge in g.getEdges():
        node1 = graph.get_node(edge.getNode1().getName())
        node2 = graph.get_node(edge.getNode2().getName())
        endpoint1 = endpoint_map[edge.getEndpoint1().name()]
        endpoint2 = endpoint_map[edge.getEndpoint2().name()]
        graph.add_edge(Edge(node1, node2, endpoint1, endpoint2))

    return graph


