import os
import time as tm
import numpy as np
import torch.nn as nn

# Must import something from pytetrad before importing Java packages, as it starts JPype.
import pytetrad.tools.TetradSearch as tets
import edu.cmu.tetrad.graph as tg

# Initialize the CausalPerceptronNetwork
import cpn as cpn

###
# This is an example of nonlinear simulation and search. The example generates a
# random DAG, simulates data from it using a neural network, and then runs the
# BOSS/BF-BIC search algorithm to recover the CPDAG. It also compares the true and
# estimated CPDAGs using graph stats in Tetrad.
###

num_nodes = 10  # The number of nodes in the random DAG
num_edges = 20  # The number of edges in the random DAG
num_samples = 1_000  # sample size to simulate i.i.d.

input_scale = 1  # Affects bumpiness of functions

show_plots = False  # True to show plots, False to not show plots

seed=None

if seed is not None:
    np.random.seed(seed)

if seed == None:
    seed_ = -1
else:
    seed_ = seed

# Generate a random DAG
true_dag = tg.RandomGraph.randomGraph(num_nodes, 0, num_edges, 100, 100, 100, False, seed_)

print(true_dag)

noise_distributions = {}
for node in true_dag.getNodes():
    noise_distributions[node] = cpn.NoiseDistribution(distribution_type="beta", alpha=2, beta=5)

cpn = cpn.CausalPerceptronNetwork(
    graph=true_dag,
    num_samples=num_samples,  # Number of data samples to generate
    noise_distributions=noise_distributions,  # Function to generate exogenous noise

    # Output not scaled if rescale_max and rescale_min are commented out.
    # rescale_min=-1, # Minimum value for rescaling each variable after simulation
    # rescale_max=1, # Maximum value for rescaling each variable after simulation
    hidden_dimensions=[50, 50, 50, 50, 50],  # Hidden layer dimensions
    input_scale=input_scale,  # Input scaling factor
    activation_module=nn.LeakyReLU(),  # Activation function
    nonlinearity='leaky_relu',  # Nonlinearity
    discrete_prob=0,  # Probability of discrete variables
    seed=seed # For reproducbiltiy. Set to 'None' for a different result each time.
)

start = tm.time()

# Simulate the data from the CPN. This returns a pandas dataframe.
df = cpn.generate_data()

# Shuffle columns to avoid order effects in search.
shuffled_columns = np.random.permutation(df.columns)
df = df[shuffled_columns]

print(df.head())

if show_plots:
    # Visualize the pairwise relationships between variables
    import matplotlib.pyplot as plt
    import seaborn as sns

    # g = sns.pairplot(df, kind='kde', diag_kind="kde", corner=True) # Need smaller sample size for this
    g = sns.pairplot(df, kind='hist', diag_kind="hist", corner=True)
    g.figure.set_size_inches(8, 8)
    g.figure.suptitle("Pairwise Relationships in Generated Data", y=1.02, fontsize=16)

    # Save the plot to a file
    g.figure.savefig("pairwise_relationships.png", dpi=300, bbox_inches="tight")

    # Show the plot
    plt.show()

# Save the Tetrad graph to a text file called "graph_nonlinear.txt" and save the data to a tab-delimited text
# file called "data_nonlinear.txt" in the current working directory
with open("graph_nonlinear.txt", "w") as f:
    f.write(str(true_dag))

df.to_csv("data_nonlinear.txt", sep="\t", index=False)

cwd = os.getcwd()
print(f"Graph saved to {cwd}/graph_nonlinear.txt")
print(f"Data saved to {cwd}/data_nonlinear.txt")
