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
# ========================================
# Analysis Parameters
# ========================================
ALGORITHM = "boss"  # Options: "boss" or "fges"
DATA_PATH = "null_variable_dt.csv"
KNOWLEDGE_FILE = "mike_knowledge_box.txt"
OUTPUT_DIR = "boss_results" if ALGORITHM == "boss" else "fges_results"
NON_NULL_OUTPUT_DIR = "boss_domain_results" if ALGORITHM == "boss" else "fges_domain_results"

# Algorithm-specific parameters
PENALTY_DISCOUNT = 2
N_BOOTSTRAP = 100 if ALGORITHM == "boss" else 50
SEED = 32

# Output control
SHOW_BOOTSTRAP_OUTPUT = False  # Set to True to see bootstrap iteration counts

# 1PNEF Threshold percentile (1st percentile = 0.01)
PNEF_PERCENTILE = 0.01

# Nodes of interest for sub-graph analysis (effort variables)
NODES_OF_INTEREST = [
    "silence", "silence2",
    "mis_link", "mis_link2",
    "code_dev", "code_dev2",
    "churn", "churn2",
    "commit", "commit2"
]

# %% [markdown]
# ## 2. Import Libraries
# 
# Load required modules for data processing and causal analysis.

# %%
# Increase Java memory allocation for large bootstrap analyses
import os
os.environ['JAVA_TOOL_OPTIONS'] = '-Xmx8g -Xms4g'  # 8GB max heap, 4GB initial
print("✓ Java memory configured: 8GB max, 4GB initial")

# %%
import pandas as pd
import json
from pykumu_helpers import (
    load_data, detect_variable_types, 
    parse_graph, prepare_non_null_dataset,
    derive_1pnef_threshold, apply_1pnef_threshold
)
from pykumu_algorithms import run_boss_analysis, run_fges_analysis
from pykumu_visualization import (
    prepare_graph_edges, plot_causal_graph, plot_subgraph,
    find_cycles, print_cycle_report
)

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
        seed=SEED,
        suppress_output=not SHOW_BOOTSTRAP_OUTPUT  # Toggle bootstrap output
    )
else:
    results = run_fges_analysis(
        data=data,
        knowledge_file=KNOWLEDGE_FILE,
        output_dir=OUTPUT_DIR,
        penalty_discount=PENALTY_DISCOUNT,
        n_bootstrap=N_BOOTSTRAP,
        seed=SEED,
        suppress_output=not SHOW_BOOTSTRAP_OUTPUT  # Toggle bootstrap output
    )

print(f"\nDiscovered: {results['n_nodes']} nodes, {results['n_edges']} edges")
print(f"Elapsed: {results['elapsed_time']:.1f}s")

# %% [markdown]
# ---
# 
# # Deriving the 1PNEF Threshold
# 
# In our causal search above, we introduced null features over multiple bootstrap runs to observe how often our causal search forms random edges (i.e. between our features and null features). We will use this information to derive a threshold, **1PNEF** (1st Percentile NoEdge Frequency), we can use in our final causal search.
# 
# ## 6. Graph Examination
# 
# We parse the Tetrad JSON graph output into tabular format: nodes, edgeset, and edge type probabilities.
# 
# The **edgeset** table contains the ensemble edge for each node pair. Because we performed multiple bootstrap runs, the probabilities represent the ensemble of all edges formed on each execution.
# 
# The **edge_type_probabilities** table shows the counts of each type of edge formed on each subgraph across all bootstrap runs.

# %%
# Parse the JSON output from null variable causal search
null_graph = parse_graph(str(results['graph_json']))

print(f"Nodes: {len(null_graph['nodes'])}")
print(f"\nFirst 5 nodes:")
print(null_graph['nodes'].head())
print(f"\nEdgeset: {len(null_graph['edgeset'])} edges")
print(null_graph['edgeset'].head())
print(f"\nEdge type probabilities: {len(null_graph['edge_type_probabilities'])} entries")
print(null_graph['edge_type_probabilities'].head())

# %% [markdown]
# ## 7. Deriving 1PNEF
# 
# Our interest is to derive a threshold for the final causal search, using the information from this bootstrapped null feature causal search. By definition, edges formed between actual variables and random (null) features represent random edges.
# 
# We:
# 1. Subset the edgeset to contain only edges where at least one node is a null variable (nv-*)
# 2. Derive a `no_edge` probability by subtracting the probability from 1
# 3. Identify the 1st percentile value of the no_edge probability → the **1PNEF threshold**
# 
# This threshold tells us: given entirely random variables, causal links were formed between them up to X% of the time. In our final search, we only keep causal links that formed **more** than X% of the time.

# %%
# Derive the 1PNEF threshold from null variable edges
pnef_1, nv_edges = derive_1pnef_threshold(null_graph['edgeset'], percentile=PNEF_PERCENTILE)

print(f"\n1PNEF Threshold: {pnef_1:.4f}")
print(f"\nSample of null variable edges:")
print(nv_edges.head(10))

# %% [markdown]
# ---
# 
# # Non-Null Causal Search
# 
# With the threshold defined, we now proceed to the final causal search, which **does not include null features**. In this non-null feature causal search, we also specify domain knowledge to prohibit causal links that don't make sense temporally (e.g. features at 1-time-lag cannot cause features in the present).
# 
# ## 8. Prepare Non-Null Dataset
# 
# Remove null variable columns (nv-*) from the dataset, keeping only the original features and binary CVE indicators.

# %%
# Prepare dataset without null variables for domain knowledge search
non_null_data = prepare_non_null_dataset(data, save_path="binarized_variable_dt.csv")

# %% [markdown]
# ## 9. Domain Knowledge Causal Search
# 
# Run the causal search on the non-null dataset with domain knowledge constraints. This search uses the same algorithm and bootstrap settings, but on the dataset **without** null features and **with** temporal knowledge constraints.

# %%
# Run domain knowledge causal search on non-null dataset
if ALGORITHM == "boss":
    domain_results = run_boss_analysis(
        data=non_null_data,
        knowledge_file=KNOWLEDGE_FILE,
        output_dir=NON_NULL_OUTPUT_DIR,
        penalty_discount=PENALTY_DISCOUNT,
        n_bootstrap=N_BOOTSTRAP,
        seed=SEED,
        suppress_output=not SHOW_BOOTSTRAP_OUTPUT
    )
else:
    domain_results = run_fges_analysis(
        data=non_null_data,
        knowledge_file=KNOWLEDGE_FILE,
        output_dir=NON_NULL_OUTPUT_DIR,
        penalty_discount=PENALTY_DISCOUNT,
        n_bootstrap=N_BOOTSTRAP,
        seed=SEED,
        suppress_output=not SHOW_BOOTSTRAP_OUTPUT
    )

print(f"\nDomain search discovered: {domain_results['n_nodes']} nodes, {domain_results['n_edges']} edges")
print(f"Elapsed: {domain_results['elapsed_time']:.1f}s")

# %% [markdown]
# ## 10. Parse Domain Search Results
# 
# Parse the domain knowledge causal search JSON output into nodes, edgeset, and edge type probabilities.

# %%
# Parse the domain search JSON output
domain_graph = parse_graph(str(domain_results['graph_json']))

print(f"Domain search nodes: {len(domain_graph['nodes'])}")
print(f"Domain search edges: {len(domain_graph['edgeset'])}")
print(f"\nEdgeset sample:")
print(domain_graph['edgeset'].head())

# %% [markdown]
# ---
# 
# # Applying 1PNEF Threshold
# 
# ## 11. Filter Edges
# 
# Edges which may have been formed at random are filtered here. We apply the 1PNEF threshold derived from the null variable search to the domain knowledge search results. Only edges whose `no_edge` probability is less than or equal to the 1PNEF threshold are kept.

# %%
# Apply 1PNEF threshold to the domain search edges
edges_1pnef = apply_1pnef_threshold(domain_graph['edgeset'], pnef_1)

print(f"\nFiltered edges (1PNEF trimmed):")
print(edges_1pnef)

# %%
# Save the 1PNEF-filtered edges
os.makedirs(NON_NULL_OUTPUT_DIR, exist_ok=True)
edges_1pnef.to_csv(f"{NON_NULL_OUTPUT_DIR}/edges_1pnef.csv", index=False)
print(f"✓ Saved filtered edges to {NON_NULL_OUTPUT_DIR}/edges_1pnef.csv")

# %% [markdown]
# ---
# 
# # Results
# 
# With the final causal graph trimmed, we can now inspect it to draw conclusions. Causal graphs may form cycles and have undirected edges.
# 
# ## 12. Full Causal Graph (1PNEF Trimmed)
# 
# Interactive visualization of the full causal graph after applying the 1PNEF threshold.
# 
# Edge colors:
# - **Black**: Directed edges (causal relationship)
# - **Red**: Undirected edges (TAIL-TAIL, association without determined direction)

# %%
# Prepare edges for visualization
viz_edges = prepare_graph_edges(edges_1pnef)

# Plot the full causal graph
full_graph = plot_causal_graph(
    edges_df=viz_edges,
    graph_nodes=domain_graph['nodes'],
    title="Full Causal Graph (1PNEF Trimmed)",
    output_html=f"{NON_NULL_OUTPUT_DIR}/causal_graph_full.html"
)

# Display in notebook (if pyvis available)
if full_graph is not None:
    full_graph.show(f"{NON_NULL_OUTPUT_DIR}/causal_graph_full.html")

# %% [markdown]
# ## 13. Sub-Graph: Effort Variables and Parents
# 
# Focus on the key effort variables and their causal relationships. This sub-graph shows only the nodes of interest and edges between them.

# %%
# Plot sub-graph for effort variables
sub_graph = plot_subgraph(
    edges_df=viz_edges,
    nodes_of_interest=NODES_OF_INTEREST,
    graph_nodes=domain_graph['nodes'],
    title="Sub-Graph: Effort Variables",
    output_html=f"{NON_NULL_OUTPUT_DIR}/causal_graph_subgraph.html",
    include_parents=False  # Set True to include parent nodes
)

if sub_graph is not None:
    sub_graph.show(f"{NON_NULL_OUTPUT_DIR}/causal_graph_subgraph.html")

# %% [markdown]
# ## 14. Cycle Detection
# 
# Check if the causal graph contains any cycles. Cycles indicate feedback loops in the causal structure.

# %%
# Detect cycles in the 1PNEF-trimmed graph
cycles = find_cycles(viz_edges)
print_cycle_report(cycles)

# %% [markdown]
# ---
# 
# ## 15. Summary
# 
# **Analysis Pipeline:**
# 1. **Null Variable Search** — Causal search with null features to observe random edge formation
# 2. **1PNEF Derivation** — Derived threshold from null variable edges (1st percentile no-edge frequency)
# 3. **Domain Knowledge Search** — Final search without null features, with temporal constraints
# 4. **1PNEF Filtering** — Removed edges that may have formed by random chance
# 5. **Visualization** — Inspected full graph, sub-graphs, and cycles
# 
# **Output Files:**
# - Null variable search results → `{OUTPUT_DIR}/`
# - Domain knowledge search results → `{NON_NULL_OUTPUT_DIR}/`
# - 1PNEF-filtered edges → `{NON_NULL_OUTPUT_DIR}/edges_1pnef.csv`
# - Interactive graphs → `{NON_NULL_OUTPUT_DIR}/*.html`



