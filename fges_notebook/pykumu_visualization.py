"""
PyKumu Visualization Functions
===============================

Network graph visualization for causal analysis results.
Matches R workflow using igraph + visNetwork from issue_causal_analysis.Rmd.

Uses networkx for graph analysis and pyvis for interactive visualization.

Author: Migrated from Kumu R package
Date: February 2026
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple


def find_cycles(edges_df: pd.DataFrame) -> List[List[str]]:
    """
    Find all cycles in a directed graph.
    
    Matches R function: find_cycles() from issue_causal_analysis.Rmd
    Uses DFS-based cycle detection.
    
    Parameters
    ----------
    edges_df : pd.DataFrame
        Edge DataFrame with 'from' and 'to' columns
        
    Returns
    -------
    list
        List of cycles, where each cycle is a list of node names
        
    Example
    -------
    >>> cycles = find_cycles(edges_df)
    >>> print(f"Found {len(cycles)} cycles")
    """
    try:
        import networkx as nx
    except ImportError:
        print("⚠️  networkx not installed. Install with: pip install networkx")
        return []
    
    G = nx.DiGraph()
    for _, row in edges_df.iterrows():
        G.add_edge(row['from'], row['to'])
    
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except Exception as e:
        print(f"⚠️  Error detecting cycles: {e}")
        return []


def prepare_graph_edges(edges_1pnef: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare edges for visualization with colors based on edge type.
    
    Matches R workflow:
    - TAIL-TAIL (undirected): red
    - All others (directed): black
    
    Parameters
    ----------
    edges_1pnef : pd.DataFrame
        Filtered edges from apply_1pnef_threshold()
        
    Returns
    -------
    pd.DataFrame
        Edges with 'from', 'to', 'color', 'weight', 'label' columns
    """
    edges = edges_1pnef.copy()
    
    # Assign color based on edge type
    edges['color'] = 'black'
    mask_undirected = (edges['endpoint1'] == 'TAIL') & (edges['endpoint2'] == 'TAIL')
    edges.loc[mask_undirected, 'color'] = 'red'
    
    # Create visualization columns
    result = pd.DataFrame({
        'from': edges['node1_name'],
        'to': edges['node2_name'],
        'color': edges['color'],
        'weight': edges['probability'],
        'label': edges['probability'].round(3).astype(str),
        'endpoint1': edges['endpoint1'],
        'endpoint2': edges['endpoint2']
    })
    
    return result


# Color scheme matching R colorBlindness::Blue2DarkRed12Steps
COLORBLIND_PALETTE = {
    1: '#2166AC',   # Blue (step 1) - binary indicators
    3: '#67A9CF',   # Light blue (step 3) - mis_link
    5: '#D1E5F0',   # Pale blue (step 5) - silence  
    7: '#FDDBC7',   # Pale orange (step 7) - code_dev
    8: '#F4A582',   # Light red (step 8) - churn
    9: '#D6604D',   # Red (step 9) - commit
    'default': '#B2182B'  # Dark red
}


def assign_node_colors(nodes: pd.DataFrame) -> pd.DataFrame:
    """
    Assign colors to nodes based on variable type.
    
    Matches R workflow color assignment from issue_causal_analysis.Rmd.
    
    Parameters
    ----------
    nodes : pd.DataFrame
        Nodes DataFrame with 'node' column
        
    Returns
    -------
    pd.DataFrame
        Nodes with 'color' column added
    """
    nodes = nodes.copy()
    nodes['color'] = COLORBLIND_PALETTE[3]  # Default: light blue
    
    # Assign by variable type
    silence_mask = nodes['node'].str.contains('silence', na=False)
    nodes.loc[silence_mask, 'color'] = COLORBLIND_PALETTE[5]
    
    mis_link_mask = nodes['node'].str.contains('mis_link', na=False)
    nodes.loc[mis_link_mask, 'color'] = COLORBLIND_PALETTE[3]
    
    code_dev_mask = nodes['node'].str.contains('code_dev', na=False)
    nodes.loc[code_dev_mask, 'color'] = COLORBLIND_PALETTE[7]
    
    churn_mask = nodes['node'].str.contains('churn', na=False)
    nodes.loc[churn_mask, 'color'] = COLORBLIND_PALETTE[8]
    
    commit_mask = nodes['node'].str.contains('commit', na=False)
    nodes.loc[commit_mask, 'color'] = COLORBLIND_PALETTE[9]
    
    binary_mask = nodes['node'].str.contains('b_', na=False)
    nodes.loc[binary_mask, 'color'] = COLORBLIND_PALETTE[1]
    
    return nodes


def plot_causal_graph(edges_df: pd.DataFrame,
                      graph_nodes: pd.DataFrame,
                      title: str = "Causal Graph",
                      output_html: Optional[str] = None,
                      height: str = "700px",
                      width: str = "100%",
                      notebook: bool = True) -> Optional[object]:
    """
    Create interactive causal graph visualization.
    
    Matches R workflow: visNetwork visualization with igraph layout.
    Uses pyvis for interactive HTML visualization.
    
    Parameters
    ----------
    edges_df : pd.DataFrame
        Edges with 'from', 'to', 'color', 'weight' columns
    graph_nodes : pd.DataFrame
        Nodes from parse_graph() with 'node_name' column
    title : str
        Graph title
    output_html : str, optional
        Path to save HTML file
    height : str
        Visualization height
    width : str
        Visualization width
    notebook : bool
        Whether running in Jupyter notebook
        
    Returns
    -------
    pyvis.network.Network or None
        Interactive network object, or None if pyvis not available
    """
    try:
        from pyvis.network import Network
    except ImportError:
        print("⚠️  pyvis not installed. Install with: pip install pyvis")
        print("Falling back to text summary.")
        _print_graph_summary(edges_df)
        return None
    
    net = Network(height=height, width=width, directed=True, 
                  notebook=notebook, cdn_resources='in_line')
    
    # Prepare nodes
    all_nodes = set(edges_df['from'].tolist() + edges_df['to'].tolist())
    
    # Also include isolated nodes from the graph
    if 'node_name' in graph_nodes.columns:
        all_nodes.update(graph_nodes['node_name'].tolist())
    elif 'node' in graph_nodes.columns:
        all_nodes.update(graph_nodes['node'].tolist())
    
    # Create node DataFrame for coloring
    nodes_for_color = pd.DataFrame({'node': list(all_nodes)})
    nodes_colored = assign_node_colors(nodes_for_color)
    
    for _, row in nodes_colored.iterrows():
        net.add_node(row['node'], label=row['node'], color=row['color'],
                     title=row['node'], size=20)
    
    # Add edges
    for _, row in edges_df.iterrows():
        arrows = ''
        if row.get('endpoint2') == 'ARROW':
            arrows = 'to'
        elif row.get('endpoint1') == 'ARROW':
            arrows = 'from'
        
        net.add_edge(row['from'], row['to'], 
                     color=row.get('color', 'black'),
                     value=float(row.get('weight', 1.0)),
                     title=f"p={row.get('weight', '')}", 
                     label=str(row.get('label', '')),
                     arrows=arrows)
    
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 200,
                "springConstant": 0.08
            },
            "solver": "forceAtlas2Based",
            "stabilization": {"iterations": 150}
        },
        "interaction": {
            "navigationButtons": true,
            "keyboard": true,
            "hover": true
        }
    }
    """)
    
    if output_html:
        net.save_graph(output_html)
        print(f"Graph saved to: {output_html}")
    
    return net


def plot_subgraph(edges_df: pd.DataFrame,
                  nodes_of_interest: List[str],
                  graph_nodes: pd.DataFrame,
                  title: str = "Sub-Graph",
                  output_html: Optional[str] = None,
                  include_parents: bool = True) -> Optional[object]:
    """
    Create sub-graph visualization for specific nodes of interest.
    
    Matches R workflow: Sub-Graphs of Effort Variables and Parents.
    
    Parameters
    ----------
    edges_df : pd.DataFrame
        Full edges DataFrame with 'from' and 'to' columns
    nodes_of_interest : list
        List of node names to include
    graph_nodes : pd.DataFrame
        All graph nodes
    title : str
        Graph title
    output_html : str, optional
        Path to save HTML file
    include_parents : bool
        Whether to include parent nodes of nodes_of_interest
        
    Returns
    -------
    pyvis.network.Network or None
    """
    # Filter edges to only those between nodes of interest
    mask = (edges_df['from'].isin(nodes_of_interest) & 
            edges_df['to'].isin(nodes_of_interest))
    
    if include_parents:
        # Also include edges from parent nodes TO nodes of interest
        parent_mask = edges_df['to'].isin(nodes_of_interest)
        mask = mask | parent_mask
    
    sub_edges = edges_df[mask].copy()
    
    if len(sub_edges) == 0:
        print(f"No edges found between specified nodes of interest.")
        return None
    
    # Get nodes that appear in sub-graph
    sub_node_names = set(sub_edges['from'].tolist() + sub_edges['to'].tolist())
    sub_nodes = pd.DataFrame({'node_name': list(sub_node_names)})
    
    print(f"Sub-graph: {len(sub_node_names)} nodes, {len(sub_edges)} edges")
    
    return plot_causal_graph(sub_edges, sub_nodes, title=title, 
                             output_html=output_html)


def _print_graph_summary(edges_df: pd.DataFrame) -> None:
    """Print text summary when visualization libraries unavailable."""
    print(f"\n{'='*60}")
    print(f"Graph Summary: {len(edges_df)} edges")
    print(f"{'='*60}")
    
    if 'color' in edges_df.columns:
        directed = len(edges_df[edges_df['color'] == 'black'])
        undirected = len(edges_df[edges_df['color'] == 'red'])
        print(f"  Directed edges: {directed}")
        print(f"  Undirected edges: {undirected}")
    
    print(f"\nTop 10 edges by probability:")
    if 'weight' in edges_df.columns:
        top = edges_df.nlargest(10, 'weight')[['from', 'to', 'weight']]
        for _, row in top.iterrows():
            print(f"  {row['from']} → {row['to']}  (p={row['weight']:.3f})")


def print_cycle_report(cycles: List[List[str]]) -> None:
    """
    Print a formatted report of cycles found in the graph.
    
    Parameters
    ----------
    cycles : list
        List of cycles from find_cycles()
    """
    if not cycles:
        print("No cycles detected in the graph.")
        return
    
    print(f"Found {len(cycles)} cycle(s):")
    for i, cycle in enumerate(cycles, 1):
        cycle_str = " → ".join(cycle) + f" → {cycle[0]}"
        print(f"  Cycle {i} (length {len(cycle)}): {cycle_str}")
