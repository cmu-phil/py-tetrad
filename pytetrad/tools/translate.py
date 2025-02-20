## This assumes that you have already started the JVM using JPype. You may
## start the JVM only once per session. Your code should start with the following
## lines:
#
import jpype
import jpype.imports

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

## Some functions wrapping various classes in Tetrad. Feel free to just steal
## the relevant code for your own projects, or 'pip install' this Github directory
## and call these functions. will add more named parameters to help one see which 
## methods for the the searches can be controlled.

# # this needs to happen before import pytetrad (otherwise lib cant be found)
# BASE_DIR = os.path.join(os.path.dirname(__file__), '../..')
# sys.path.append(BASE_DIR)

import numpy as np
import pandas as pd
from pandas import DataFrame

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg


def pandas_data_to_tetrad(df: DataFrame, int_as_cont=False):
    dtypes = ["float16", "float32", "float64"]
    if int_as_cont:
        for i in range(3, 7):
            dtypes.append(f"int{2 ** i}")
            dtypes.append(f"uint{2 ** i}")
    cols = df.columns
    discrete_cols = [col for col in cols if df[col].dtypes not in dtypes]
    category_map = {col: {val: i for i, val in enumerate(df[col].unique())} for col in discrete_cols}
    df = df.replace(category_map)
    values = df.values
    n, p = df.shape

    variables = util.ArrayList()
    for col in cols:
        if col in discrete_cols:
            categories = util.ArrayList()
            for category in category_map[col]:
                categories.add(str(category))
            variables.add(td.DiscreteVariable(str(col), categories))
        else:
            variables.add(td.ContinuousVariable(str(col)))

    if len(discrete_cols) == len(cols):
        databox = td.IntDataBox(n, p)
    elif len(discrete_cols) == 0:
        databox = td.DoubleDataBox(n, p)
    else:
        databox = td.MixedDataBox(variables, n)

    for col, var in enumerate(values.T):
        for row, val in enumerate(var):
            databox.set(row, col, val)

    return td.BoxDataSet(databox, variables)


def tetrad_data_to_pandas(data: td.DataSet):
    names = data.getVariableNames()
    columns_ = []

    for name in names:
        columns_.append(str(name))

    df: DataFrame = pd.DataFrame(columns=columns_, index=range(data.getNumRows()))

    for row in range(data.getNumRows()):
        for col in range(data.getNumColumns()):
            df.at[row, columns_[col]] = data.getObject(row, col)

    return df

## The defaults here are for the PCALG style of general graph endpoint matrices, but
## the user can use whichever endpoint encoding they like.
def graph_to_matrix(g, nullEpt = 0, circleEpt = 1, arrowEpt = 2, tailEpt = 3):
    endpoint_map = {"NULL": nullEpt,
                    "CIRCLE": circleEpt,
                    "ARROW": arrowEpt,
                    "TAIL": tailEpt}

    nodes = g.getNodes()
    p = g.getNumNodes()
    A = np.zeros((p, p), dtype=int)

    for edge in g.getEdges():
        i = nodes.indexOf(edge.getNode1())
        j = nodes.indexOf(edge.getNode2())
        A[j][i] = endpoint_map[edge.getEndpoint1().name()]
        A[i][j] = endpoint_map[edge.getEndpoint2().name()]

    columns_ = []

    for name in nodes:
        columns_.append(str(name))

    return pd.DataFrame(A, columns=columns_)

def tetrad_matrix_to_numpy(array):
    # print(array)
    #
    # print("rows = ", array.getNumRows())
    # print("cols = ", array.getNumColumns())

    np_array = np.zeros((array.getNumRows(), array.getNumColumns()), dtype=float)

    for i in range(array.getNumRows()):
        for j in range(array.getNumColumns()):
            np_array[i][j] = array.get(i, j)

    return np_array

def tetrad_matrix_to_pandas(array, variables):
    np_array = tetrad_matrix_to_numpy(array)
    columns = [str(variables.get(i)) for i in range(array.getNumColumns())]
    return pd.DataFrame(np_array, columns=columns)

# Input a square int[][] array with only 0's and 1's, where a[i][j] = 1 just in case
# j->i. Returns a Java graph object for this.
def adj_matrix_to_graph(adjMatrix):
    rows, cols = adjMatrix.shape

    if rows != cols:
        raise ValueError("The matrix is not square. Rows and columns must be equal.")

    variable_names = ["X" + str(i) for i in range(1, rows + 1)]
    variables = util.ArrayList()

    for i in range(0, rows):
        variables.append(tg.GraphNode(variable_names[i]))

    graph = tg.EdgeListGraph(variables)

    for i, row in enumerate(adjMatrix):
        for j, value in enumerate(row):
            if (adjMatrix[i][j]):
                graph.addDirectedEdge(variables.get(i), variables.get(j))

    return graph


# PASS ME A GraphViz Graph object and call it gdot!
def write_gdot(g, gdot):
    endpoint_map = {"TAIL": "none",
                    "ARROW": "empty",
                    "CIRCLE": "odot"}

    for node in g.getNodes():
        gdot.node(str(node.getName()),
                  shape='circle',
                  fixedsize='true',
                  style='filled',
                  color='lightgray')

    for edge in g.getEdges():
        node1 = str(edge.getNode1().getName())
        node2 = str(edge.getNode2().getName())
        endpoint1 = str(endpoint_map[edge.getEndpoint1().name()])
        endpoint2 = str(endpoint_map[edge.getEndpoint2().name()])
        color = "blue"
        if (endpoint1 == "empty") and (endpoint2 == "empty"): color = "red"
        gdot.edge(node1, node2,
                  arrowtail=endpoint1,
                  arrowhead=endpoint2,
                  dir='both', color=color)

    return gdot

# Prints a Java graph object as a Tetrad-style string. Needed from R.
def print_java(java_graph: tg.Graph):
    print(java_graph)
