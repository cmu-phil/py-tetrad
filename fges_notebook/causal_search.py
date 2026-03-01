# %% [markdown]
# # Causal Discovery Analysis
# 
# Causal search using BOSS/FGES algorithms via PyTetrad.
# 
# **Reference:** Kumu R package, `issue_causal_analysis.Rmd` (Stage 5: Causal Search)


# %% [markdown]
# ## 1. Configuration
# 
# Set algorithm parameters and file paths.

# %%
# Analysis parameters
ALGORITHM = "boss"  # Options: "boss" or "fges"
DATA_PATH = "null_variable_dt.csv"
KNOWLEDGE_FILE = "mike_knowledge_box.txt"
OUTPUT_DIR = "boss_results" if ALGORITHM == "boss" else "fges_results"

# Algorithm-specific parameters
PENALTY_DISCOUNT = 2
N_BOOTSTRAP = 1000 if ALGORITHM == "boss" else 500
SEED = 32



# %% [markdown]
# ## 2. Import Libraries
# 
# Load required modules for data processing and causal analysis.

# %%
import pandas as pd
from pykumu_helpers import load_data, detect_variable_types
from pykumu_algorithms import run_boss_analysis, run_fges_analysis

# %%
# Reload modules to pick up code changes
import importlib
import sys
if 'pykumu_algorithms' in sys.modules:
    importlib.reload(sys.modules['pykumu_algorithms'])
if 'pykumu_helpers' in sys.modules:
    importlib.reload(sys.modules['pykumu_helpers'])
print("Modules reloaded")



# %% [markdown]
# ## 3. Load Data
# 
# Read dataset and validate data quality.

# %%
data = load_data(DATA_PATH)
print(f"Dataset: {data.shape[0]} rows × {data.shape[1]} columns")



# %% [markdown]
# ## 4. Variable Analysis
# 
# Identify binary CVE indicators, continuous metrics, and null variables.

# %%
var_types = detect_variable_types(data)
print(f"Binary indicators: {len(var_types['cve_indicators'])}")
print(f"Continuous metrics: {len(var_types['metrics'])}")
print(f"Null variables: {len(var_types['null_variables'])}")



# %% [markdown]
# ## 5. Causal Search
# 
# Executes causal discovery with bootstrapping and domain knowledge constraints.

# %%
# Execute algorithm
if ALGORITHM == "boss":
    results = run_boss_analysis(
        data=data,
        knowledge_file=KNOWLEDGE_FILE,
        output_dir=OUTPUT_DIR,
        penalty_discount=PENALTY_DISCOUNT,
        n_bootstrap=N_BOOTSTRAP,
        seed=SEED
    )
else:
    results = run_fges_analysis(
        data=data,
        knowledge_file=KNOWLEDGE_FILE,
        output_dir=OUTPUT_DIR,
        penalty_discount=PENALTY_DISCOUNT,
        n_bootstrap=N_BOOTSTRAP,
        seed=SEED
    )

print(f"\nDiscovered: {results['n_nodes']} nodes, {results['n_edges']} edges")
print(f"Elapsed: {results['elapsed_time']:.1f}s")



# %% [markdown]
# ## 6. Results Summary
# 
# Examine discovered edges and their directionality.

# %%
edges_df = results['edges']
print(f"Total edges: {len(edges_df)}")
print(f"\nEdge types:")
print(f"  Directed (2→3): {len(edges_df[(edges_df['Endpoint_From']==2) & (edges_df['Endpoint_To']==3)])}")
print(f"  Directed (3→2): {len(edges_df[(edges_df['Endpoint_From']==3) & (edges_df['Endpoint_To']==2)])}")
print(f"  Undirected (3—3): {len(edges_df[(edges_df['Endpoint_From']==3) & (edges_df['Endpoint_To']==3)])}")

print(f"\nFirst 10 edges:")
edges_df.head(10)



# %% [markdown]
# ## 7. Adjacency Matrix
# 
# Matrix representation of graph structure (0=none, 1=circle, 2=arrow, 3=tail).

# %%
adjacency = results['adjacency_matrix']
print(f"Adjacency matrix: {adjacency.shape[0]}×{adjacency.shape[1]}")
adjacency.iloc[:5, :5]



# %% [markdown]
# ## 8. Graph String
# 
# Text representation of the causal graph.

# %%
graph_str = str(results['graph_string'])
print(f"Graph representation ({len(graph_str)} characters):")
print(graph_str[:500] + "...")



# %% [markdown]
# ---
# 
# ## 9. Output Files
# 
# Results saved to:
# - `{OUTPUT_DIR}/adjacency_matrix.csv`
# - `{OUTPUT_DIR}/edge_list.csv`
# - `{OUTPUT_DIR}/graph_string.txt`


