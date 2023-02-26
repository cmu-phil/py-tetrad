import numpy as np

from causallearn.graph.GeneralGraph import GeneralGraph
from causallearn.graph.GraphNode import GraphNode
from causallearn.graph.Endpoint import Endpoint
from causallearn.graph.Edge import Edge

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
    endpoint_map = {"NULL": 0,
                    "CIRCLE": 1,
                    "ARROW": 2,
                    "TAIL": 3}

    nodes = g.getNodes()
    p = g.getNumNodes()
    A = np.zeros((p, p), dtype=int)

    for edge in g.getEdges():
        i = nodes.indexOf(edge.getNode1())
        j = nodes.indexOf(edge.getNode2())
        A[j][i] = endpoint_map[edge.getEndpoint1().name()]
        A[i][j] = endpoint_map[edge.getEndpoint2().name()]

    return A


def tetrad_graph_to_causal_learn(g):
    endpoint_map = {"TAIL": Endpoint.TAIL,
                    "NULL": Endpoint.NULL,
                    "ARROW": Endpoint.ARROW,
                    "CIRCLE": Endpoint.CIRCLE,
                    "STAR": Endpoint.STAR}

    nodes = [GraphNode(str(node.getName())) for node in g.getNodes()]
    graph = GeneralGraph(nodes)

    for edge in g.getEdges():
        node1 = graph.get_node(edge.getNode1().getName())
        node2 = graph.get_node(edge.getNode2().getName())
        endpoint1 = endpoint_map[edge.getEndpoint1().name()]
        endpoint2 = endpoint_map[edge.getEndpoint2().name()]
        graph.add_edge(Edge(node1, node2, endpoint1, endpoint2))

    return graph


