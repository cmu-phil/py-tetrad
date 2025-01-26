import pytetrad.tools.TetradSearch as ts
import numpy as np
import pandas as pd

# Load a dataset from a file
df = pd.read_csv("resources/mimbuild_example_data.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

# Calculate the covariance matrix of df.
cov = np.cov(df, rowvar=False)

# Make a clustering. This is a list over lists of variable indices.
clustering = [[1, 2, 3, 4], [5, 6, 8], [10, 11, 12, 13], [16, 17, 18, 19], [20, 21, 22, 23, 24]]

# Make a list of measure names. These are the variable names.
measure_names = list(df.columns)

# Make a list of latent variable names. These are the names associated with the above clusters.
latent_names = ['L1', 'L2', 'L3', 'L4', 'L5']

# Do the search.
graph = ts.mimbuild(clustering, measure_names, latent_names, cov, full_graph=False)

# Print the graph.
print(graph)
