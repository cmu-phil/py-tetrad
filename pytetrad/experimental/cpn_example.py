import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import torch.nn as nn

import CausalPerceptronNetwork as cpn

### EXPERIMENTAL ###

def custom_noise(size):
    return np.random.beta(2, 5, size)
    # return np.random.normal(0, .3, size)


# Create a random DAG
def create_random_dag(num_nodes=5, num_edges=8):
    """
    Generate a random directed acyclic graph (DAG) with a specified number
    of nodes and edges. The function ensures that no cycles are introduced
    while adding edges, preserving the acyclic property of the graph.

    :param num_nodes: The number of nodes to generate in the graph.
    :type num_nodes: int
    :param num_edges: The number of edges to generate in the graph. The function
                      attempts to create the specified number of edges while ensuring
                      the graph remains acyclic.
    :type num_edges: int
    :return: A directed acyclic graph (DAG) with the specified number of nodes and edges.
    :rtype: networkx.DiGraph
    """
    graph = nx.DiGraph()
    nodes = [f"X{i + 1}" for i in range(num_nodes)]
    graph.add_nodes_from(nodes)

    while graph.number_of_edges() < num_edges:
        u, v = np.random.choice(nodes, 2, replace=False)
        if not graph.has_edge(u, v) and not graph.has_edge(v, u):
            if not nx.has_path(graph, v, u):  # Ensure no cycles
                graph.add_edge(u, v)
    return graph


# Generate a random DAG
dag = create_random_dag(num_nodes=10, num_edges=10)

# Initialize the CausalPerceptronNetwork
cpn = cpn.CausalPerceptronNetwork(
    graph=dag,
    num_samples=1000,  # Number of data samples to generate
    noise_distribution=custom_noise, # Function to generate exogenous noise
    rescale_min=1, # Minimum value for rescaling each variable after simulation
    rescale_max=1, # Maximum value for rescaling each variable after simulation
    hidden_dimensions=[20], # Hidden layer dimensions
    input_scale=10,  # Input scaling factor
    activation_module=nn.LeakyReLU(negative_slope=0.01)  # Activation function
)

# Generate synthetic data
data = cpn.generate_data()

# Convert to a Pandas DataFrame for easier visualization
column_names = list(dag.nodes)
df = pd.DataFrame(data, columns=column_names)

# Print the first few rows of the dataset
print("Generated Data (First 5 Rows):")
print(df.head())

def tetrad_graph_string(graph):
    """
    Generates a string representation for a given graph's nodes and edges. The
    representation includes a list of all nodes in the graph, followed by an
    enumerated list of all edges in the format "source --> target".

    The function ensures that the output string is formatted for readability
    and separates the nodes and edges into distinct sections.

    :param graph: A graph object containing nodes and edges, which should be
        iterable structures supported by the `nodes` and `edges` methods.
    :type graph: Any graph-like object with `nodes` and `edges` methods.
    :return: A formatted string representation of the graph's nodes and edges.
    :rtype: str
    """
    graph_str = f"Graph Nodes:\n{';'.join(graph.nodes)}\n\nGraph Edges:\n"
    for i, (u, v) in enumerate(graph.edges(), 1):
        graph_str += f"{i}. {u} --> {v}\n"
    return graph_str


# Visualize the DAG
plt.figure(figsize=(8, 6))
nx.draw(dag, pos=nx.circular_layout(dag), with_labels=True, node_color='lightblue', node_size=3000, font_size=15,
        font_weight="bold", arrowsize=20)
plt.title("Random DAG", fontsize=18)
plt.show()

# Visualize the pairwise relationships between variables
import seaborn as sns
sns.pairplot(df, diag_kind="kde", corner=True)
plt.suptitle("Pairwise Relationships in Generated Data", y=1.02, fontsize=16)
plt.show()

# import plotly.express as px
# fig = px.scatter_matrix(data, width=800, height=800, title="Plot Matrix of Simulated Data")
# fig.update_traces(marker=dict(size=1))  # Adjust the size value as needed
# fig.show()

# Save the Tetrad graph to a text file called "graph_nonlinear.txt" and save the data to a tab-delimited text
# file called "data_nonlinear.txt" in the current working directory
with open("graph_nonlinear.txt", "w") as f:
    f.write(tetrad_graph_string(dag))

df.to_csv("data_nonlinear.txt", sep="\t", index=False)

# Print the locations of the saved files

cwd = os.getcwd()
print(f"Graph saved to {cwd}/graph_nonlinear.txt")
print(f"Data saved to {cwd}/data_nonlinear.txt")
