import pytetrad.tools.TetradSearch as ts
import edu.cmu.tetrad.search as search
import numpy as np
import pandas as pd

# Load a dataset from a file
# df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = pd.read_csv("resources/sample_lng_data_10_2_1000.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

# Create a Mimbuild object.
mb = search.Mimbuild()

# Calculate the covariance matrix of df.
cov = np.cov(df, rowvar=False)

# Make a clustering. This is a list over lists of variable indices.
clustering = [[0, 1, 2], [3, 4, 5]]

# Make a list of measure names. These are the variable names.
measure_names = list(df.columns)

# Make a list of latent variable names. These are the names associated with the above clusters.
latent_names = ['L1', 'L2']

# Do the search.
graph = ts.mimbuild(clustering, measure_names, latent_names, cov)

# Print the graph.
print(graph)
