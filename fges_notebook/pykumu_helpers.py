"""
PyKumu Helper Functions
=======================

Helper functions for causal analysis matching Kumu's R implementation.
This module provides utilities for data loading, configuration, validation,
graph parsing, and threshold derivation.

Author: Migrated from Kumu R package
Date: February 2026
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Optional, Dict, Tuple, List
import pytetrad.tools.TetradSearch as ts


def load_data(data_path: str, validate: bool = True) -> pd.DataFrame:
    """
    Load dataset for causal analysis.
    
    Matches R function: fread() with validation
    
    Parameters
    ----------
    data_path : str
        Path to CSV file
    validate : bool
        Whether to validate data quality
        
    Returns
    -------
    pd.DataFrame
        Loaded dataset as float64
        
    Example
    -------
    >>> data = load_data("null_variable_dt.csv")
    >>> print(f"Loaded {data.shape[0]} rows × {data.shape[1]} columns")
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    data = pd.read_csv(data_path)
    
    # Convert all columns to float64 (required for SEM-BIC)
    data = data.astype({col: "float64" for col in data.columns})
    
    if validate:
        _validate_data_quality(data)
    
    return data


def _validate_data_quality(data: pd.DataFrame) -> None:
    """Internal validation of data quality."""
    n_missing = data.isnull().sum().sum()
    if n_missing > 0:
        print(f"⚠️  Warning: {n_missing} missing values detected")
    
    # Check for constant columns (no variance)
    constant_cols = [col for col in data.columns if data[col].nunique() == 1]
    if constant_cols:
        print(f"⚠️  Warning: {len(constant_cols)} constant columns (no variance)")


def detect_variable_types(data: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Detect binary CVE indicators vs continuous metrics.
    
    Matches R workflow: Binary indicator detection
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataset to analyze
        
    Returns
    -------
    dict
        Dictionary with keys:
        - 'binary': List of binary column names (CVE indicators)
        - 'continuous': List of continuous column names (metrics)
        - 'null_variables': List of null variable column names (nv-*)
        
    Example
    -------
    >>> var_types = detect_variable_types(data)
    >>> print(f"Binary CVE indicators: {len(var_types['binary'])}")
    >>> print(f"Continuous metrics: {len(var_types['continuous'])}")
    """
    binary_cols = [col for col in data.columns 
                   if set(data[col].dropna().unique()).issubset({0, 1, 0.0, 1.0})]
    
    null_vars = [col for col in data.columns if col.startswith('nv-')]
    
    continuous_cols = [col for col in data.columns 
                      if col not in binary_cols]
    
    return {
        'binary': binary_cols,
        'continuous': continuous_cols,
        'null_variables': null_vars,
        'cve_indicators': [col for col in binary_cols if col.startswith('b_')],
        'metrics': [col for col in continuous_cols if not col.startswith('nv-')]
    }


def configure_sem_bic(search: ts.TetradSearch, 
                      penalty_discount: float = 2,
                      sem_bic_rule: int = 1,
                      structure_prior: float = 0) -> ts.TetradSearch:
    """
    Configure SEM-BIC score for causal search.
    
    Matches R function: score_sem_bic()
    
    Parameters
    ----------
    search : TetradSearch
        Initialized TetradSearch object
    penalty_discount : float
        Penalty for model complexity (higher = prefer simpler models)
    sem_bic_rule : int
        Lambda calculation: 1=Chickering (default), 2=Nandy
    structure_prior : float
        Prior belief about graph structure (0 = no prior)
        
    Returns
    -------
    TetradSearch
        Configured search object
        
    Example
    -------
    >>> search = ts.TetradSearch(data)
    >>> search = configure_sem_bic(search, penalty_discount=2)
    """
    search.use_sem_bic(
        penalty_discount=penalty_discount,
        sem_bic_rule=sem_bic_rule,
        structurePrior=structure_prior,
        singularity_lambda=0.0
    )
    return search


def configure_bootstrapping(search: ts.TetradSearch,
                           algorithm: str = "boss",
                           number_resampling: int = 1000,
                           seed: int = 32,
                           add_original: bool = True,
                           with_replacement: bool = True,
                           resampling_ensemble: int = 1) -> ts.TetradSearch:
    """
    Configure bootstrapping parameters.
    
    Matches R function: bootstrapping()
    
    Parameters
    ----------
    search : TetradSearch
        Initialized TetradSearch object
    algorithm : str
        "boss" (100% resample) or "fges" (90% resample)
    number_resampling : int
        Number of bootstrap iterations (1000 for BOSS, 500 for FGES)
    seed : int
        Random seed for reproducibility
    add_original : bool
        Include full dataset alongside resamples
    with_replacement : bool
        Bootstrap sampling with replacement
    resampling_ensemble : int
        Ensemble method: 1=Preserved, 2=Highest, 3=Majority
        
    Returns
    -------
    TetradSearch
        Configured search object
        
    Example
    -------
    >>> search = configure_bootstrapping(search, algorithm="boss")
    """
    # Algorithm-specific resample size
    # BOSS uses 100% because it has internal randomization
    # FGES uses 90% for variation
    if algorithm.lower() == "boss":
        percent_resample_size = 100
        if number_resampling != 1000:
            print(f"ℹ️  Note: Using {number_resampling} iterations (standard for BOSS: 1000)")
    elif algorithm.lower() == "fges":
        percent_resample_size = 90
        if number_resampling != 500:
            print(f"ℹ️  Note: Using {number_resampling} iterations (standard for FGES: 500)")
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Use 'boss' or 'fges'")
    
    search.set_bootstrapping(
        numberResampling=number_resampling,
        percent_resample_size=percent_resample_size,
        seed=seed,
        add_original=add_original,
        with_replacement=with_replacement,
        resampling_ensemble=resampling_ensemble
    )
    return search


def load_knowledge_constraints(search: ts.TetradSearch,
                              data: pd.DataFrame,
                               knowledge_file: Optional[str] = None) -> Tuple[ts.TetradSearch, Optional[Dict]]:
    """
    Load knowledge constraints from file.
    
    Matches R function: knowledge_file_path()
    
    Parameters
    ----------
    search : TetradSearch
        Initialized TetradSearch object
    data : pd.DataFrame
        Dataset for validating knowledge variables
    knowledge_file : str, optional
        Path to knowledge file, or None to run without constraints
        
    Returns
    -------
    tuple
        (search, validation_info) where validation_info contains matched variables
        
    Example
    -------
    >>> search, info = load_knowledge_constraints(search, data, "knowledge_box.txt")
    >>> print(f"{info['n_matched']}/{info['n_total']} variables matched")
    """
    if not knowledge_file:
        print("Running without knowledge constraints")
        return search, None
    
    if not os.path.exists(knowledge_file):
        print(f"⚠️  Knowledge file not found: {knowledge_file}")
        return search, None
    
    # Load knowledge
    search.load_knowledge(knowledge_file)
    
    # Validate variables (get from search object)
    knowledge_var_names = [str(var) for var in search.knowledge.getVariables()]
    
    # Get dataset columns from data DataFrame
    dataset_cols = set(data.columns)
    matched = [v for v in knowledge_var_names if v in dataset_cols]
    missing = [v for v in knowledge_var_names if v not in dataset_cols]
    
    validation_info = {
        'n_matched': len(matched),
        'n_total': len(knowledge_var_names),
        'matched_vars': matched,
        'missing_vars': missing
    }
    
    print(f"Knowledge loaded: {len(matched)}/{len(knowledge_var_names)} variables matched dataset")
    
    if missing:
        print(f"⚠️  {len(missing)} knowledge variables not in dataset")
    
    return search, validation_info


def configure_boss_search(data: pd.DataFrame,
                         knowledge_file: Optional[str] = None,
                         penalty_discount: float = 2,
                         n_bootstrap: int = 1000,
                         seed: int = 32,
                         time_lag: int = 0,
                         verbose: bool = False) -> ts.TetradSearch:
    """
    Configure complete BOSS search with standard settings.
    
    Matches R workflow: Combines score_sem_bic() + bootstrapping() + algorithm_boss()
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataset for causal analysis
    knowledge_file : str, optional
        Path to knowledge constraints file
    penalty_discount : float
        SEM-BIC penalty discount
    n_bootstrap : int
        Number of bootstrap iterations
    seed : int
        Random seed for reproducibility
    time_lag : int
        Time lag for time-series data (0 = no lag)
    verbose : bool
        Print detailed output
        
    Returns
    -------
    TetradSearch
        Fully configured search object ready for execution
        
    Example
    -------
    >>> search = configure_boss_search(data, knowledge_file="knowledge.txt")
    >>> # Now ready to run: search.run_boss(...)
    """
    # Initialize
    search = ts.TetradSearch(data)
    
    # Configure score
    search = configure_sem_bic(search, penalty_discount=penalty_discount)
    
    # Configure bootstrapping (BOSS-specific)
    search = configure_bootstrapping(search, algorithm="boss", 
                                    number_resampling=n_bootstrap, seed=seed)
    
    # Set algorithm parameters
    search.set_time_lag(time_lag=time_lag)
    search.set_verbose(verbose=verbose)
    
    # Load knowledge constraints
    search, _ = load_knowledge_constraints(search, data, knowledge_file)
    
    return search


def configure_fges_search(data: pd.DataFrame,
                         knowledge_file: Optional[str] = None,
                         penalty_discount: float = 2,
                         n_bootstrap: int = 500,
                         seed: int = 32,
                         time_lag: int = 0,
                         verbose: bool = False) -> ts.TetradSearch:
    """
    Configure complete FGES search with standard settings.
    
    Matches R workflow: Combines score_sem_bic() + bootstrapping() + algorithm_fges()
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataset for causal analysis
    knowledge_file : str, optional
        Path to knowledge constraints file
    penalty_discount : float
        SEM-BIC penalty discount
    n_bootstrap : int
        Number of bootstrap iterations (500 for FGES)
    seed : int
        Random seed for reproducibility
    time_lag : int
        Time lag for time-series data (0 = no lag)
    verbose : bool
        Print detailed output
        
    Returns
    -------
    TetradSearch
        Fully configured search object ready for execution
        
    Example
    -------
    >>> search = configure_fges_search(data, knowledge_file="knowledge.txt")
    >>> # Now ready to run: search.run_fges(...)
    """
    # Initialize
    search = ts.TetradSearch(data)
    
    # Configure score
    search = configure_sem_bic(search, penalty_discount=penalty_discount)
    
    # Configure bootstrapping (FGES-specific: 90% resample)
    search = configure_bootstrapping(search, algorithm="fges", 
                                    number_resampling=n_bootstrap, seed=seed)
    
    # Set algorithm parameters
    search.set_time_lag(time_lag=time_lag)
    search.set_verbose(verbose=verbose)
    
    # Load knowledge constraints
    search, _ = load_knowledge_constraints(search, data, knowledge_file)
    
    return search

# =============================================================================
# Graph Parsing Functions (matches R parse_graph())
# =============================================================================

def parse_graph(graph_json_str: str) -> Dict[str, pd.DataFrame]:
    """
    Parse Tetrad JSON graph into nodes, edgeset, and edge_type_probabilities.
    
    Matches R function: parse_graph() from kumu/R/graph.R
    
    The edgeset table contains the ensemble edge (highest probability edge type)
    for each node pair. The probability is the sum of all non-nil edge type
    probabilities.
    
    Parameters
    ----------
    graph_json_str : str
        JSON string from TetradSearch.get_json()
        
    Returns
    -------
    dict
        Dictionary with keys:
        - 'nodes': DataFrame with column 'node_name'
        - 'edgeset': DataFrame with columns: node1_name, node2_name, 
          endpoint1, endpoint2, bold, highlighted, properties, probability
        - 'edge_type_probabilities': DataFrame with columns: node1_name,
          node2_name, edge_type, properties, probability
          
    Example
    -------
    >>> graph_json = search.get_json()
    >>> graph = parse_graph(str(graph_json))
    >>> print(graph['nodes'].head())
    >>> print(graph['edgeset'].head())
    """
    graph_data = json.loads(str(graph_json_str))
    
    # Parse Nodes
    nodes = pd.DataFrame({
        'node_name': [node['name'] for node in graph_data.get('nodes', [])]
    })
    
    # Parse EdgeSet and EdgeTypeProbabilities
    edgeset_rows = []
    edge_type_prob_rows = []
    
    for edge in graph_data.get('edgesSet', []):
        node1_name = edge['node1']['name']
        node2_name = edge['node2']['name']
        endpoint1 = edge.get('endpoint1', '')
        endpoint2 = edge.get('endpoint2', '')
        bold = edge.get('bold', False)
        highlighted = edge.get('highlighted', False)
        properties = ';'.join(edge.get('properties', []))
        probability = edge.get('probability', 1.0)
        
        edgeset_rows.append({
            'node1_name': node1_name,
            'node2_name': node2_name,
            'endpoint1': endpoint1,
            'endpoint2': endpoint2,
            'bold': bold,
            'highlighted': highlighted,
            'properties': properties if properties else None,
            'probability': probability
        })
        
        # Parse edgeTypeProbabilities (only present in bootstrap/multi-run graphs)
        for etp in edge.get('edgeTypeProbabilities', []):
            edge_type = etp.get('edgeType', '')
            etp_properties = ';'.join(etp.get('properties', []))
            etp_probability = etp.get('probability', 0.0)
            
            edge_type_prob_rows.append({
                'node1_name': node1_name,
                'node2_name': node2_name,
                'edge_type': edge_type,
                'properties': etp_properties if etp_properties else None,
                'probability': etp_probability
            })
    
    edgeset = pd.DataFrame(edgeset_rows) if edgeset_rows else pd.DataFrame(
        columns=['node1_name', 'node2_name', 'endpoint1', 'endpoint2',
                 'bold', 'highlighted', 'properties', 'probability'])
    
    edge_type_probabilities = pd.DataFrame(edge_type_prob_rows) if edge_type_prob_rows else pd.DataFrame(
        columns=['node1_name', 'node2_name', 'edge_type', 'properties', 'probability'])
    
    return {
        'nodes': nodes,
        'edgeset': edgeset,
        'edge_type_probabilities': edge_type_probabilities
    }


def parse_graph_from_file(filepath: str) -> Dict[str, pd.DataFrame]:
    """
    Parse Tetrad JSON graph from file.
    
    Convenience wrapper around parse_graph() for loading from disk.
    
    Parameters
    ----------
    filepath : str
        Path to JSON graph file
        
    Returns
    -------
    dict
        Same as parse_graph()
    """
    with open(filepath, 'r') as f:
        return parse_graph(f.read())


# =============================================================================
# 1PNEF Threshold Functions (matches R random_causality_threshold.Rmd)
# =============================================================================

def derive_1pnef_threshold(edgeset: pd.DataFrame, 
                           percentile: float = 0.01) -> Tuple[float, pd.DataFrame]:
    """
    Derive 1PNEF (1st Percentile NoEdge Frequency) threshold from null variable edges.
    
    Matches R workflow in issue_causal_analysis.Rmd:
    1. Filter edges involving null variables (nv-*)
    2. Compute no_edge = 1 - probability
    3. Take the specified percentile of no_edge values
    
    The threshold tells us: given entirely random variables, causal links
    were formed between them up to (1 - threshold) of the time. In the
    final causal search, we only keep links formed MORE than that.
    
    Parameters
    ----------
    edgeset : pd.DataFrame
        Edgeset table from parse_graph() containing 'node1_name', 
        'node2_name', and 'probability' columns
    percentile : float
        Percentile for threshold (default: 0.01 = 1st percentile)
        
    Returns
    -------
    tuple
        (pnef_threshold, nv_edges_df) where:
        - pnef_threshold: The 1PNEF threshold value
        - nv_edges_df: DataFrame of null variable edges with 'no_edge' column
        
    Example
    -------
    >>> graph = parse_graph(json_str)
    >>> pnef_1, nv_edges = derive_1pnef_threshold(graph['edgeset'])
    >>> print(f"1PNEF threshold: {pnef_1:.4f}")
    """
    nv_edges = edgeset.copy()
    
    # Filter edges where at least one node is a null variable (nv-*)
    is_node1_nv = nv_edges['node1_name'].str.startswith('nv-')
    is_node2_nv = nv_edges['node2_name'].str.startswith('nv-')
    nv_edges = nv_edges[is_node1_nv | is_node2_nv].copy()
    
    if len(nv_edges) == 0:
        print("⚠️  No null variable edges found. Cannot derive 1PNEF threshold.")
        return 0.0, nv_edges
    
    # Compute no_edge probability
    nv_edges['no_edge'] = 1 - nv_edges['probability']
    
    # Derive threshold at given percentile
    pnef_threshold = nv_edges['no_edge'].quantile(percentile)
    
    print(f"Null variable edges: {len(nv_edges)}")
    print(f"1PNEF threshold (percentile={percentile}): {pnef_threshold:.4f}")
    print(f"  → Random edges formed up to {(1 - pnef_threshold)*100:.1f}% of the time")
    print(f"  → Keep only edges with probability > {(1 - pnef_threshold)*100:.1f}%")
    
    return pnef_threshold, nv_edges


def apply_1pnef_threshold(edgeset: pd.DataFrame, 
                          pnef_threshold: float) -> pd.DataFrame:
    """
    Apply 1PNEF threshold to filter edges from a causal graph.
    
    Removes edges that may have formed by random chance, keeping only
    those with no_edge probability <= the 1PNEF threshold.
    
    Parameters
    ----------
    edgeset : pd.DataFrame
        Edgeset table from parse_graph()
    pnef_threshold : float
        1PNEF threshold from derive_1pnef_threshold()
        
    Returns
    -------
    pd.DataFrame
        Filtered edgeset with only significant edges
        
    Example
    -------
    >>> edges_1pnef = apply_1pnef_threshold(graph['edgeset'], pnef_1)
    >>> print(f"Kept {len(edges_1pnef)} significant edges")
    """
    edges = edgeset.copy()
    edges['no_edge'] = 1 - edges['probability']
    
    n_before = len(edges)
    edges_filtered = edges[edges['no_edge'] <= pnef_threshold].copy()
    n_after = len(edges_filtered)
    
    print(f"Edges before threshold: {n_before}")
    print(f"Edges after 1PNEF threshold: {n_after}")
    print(f"Removed: {n_before - n_after} edges (potentially random)")
    
    return edges_filtered


# =============================================================================
# Non-Null Dataset Preparation
# =============================================================================

def prepare_non_null_dataset(data: pd.DataFrame, 
                             save_path: Optional[str] = None) -> pd.DataFrame:
    """
    Remove null variables (nv-*) from dataset for non-null causal search.
    
    Matches R workflow: Creates binarized_lag_dt without null features
    for the domain knowledge causal search.
    
    Parameters
    ----------
    data : pd.DataFrame
        Full dataset including null variables
    save_path : str, optional
        Path to save the non-null dataset CSV
        
    Returns
    -------
    pd.DataFrame
        Dataset without null variable columns
        
    Example
    -------
    >>> non_null_data = prepare_non_null_dataset(data, save_path="binarized_variable_dt.csv")
    """
    nv_cols = [col for col in data.columns if col.startswith('nv-')]
    non_null_data = data.drop(columns=nv_cols)
    
    print(f"Removed {len(nv_cols)} null variable columns")
    print(f"Non-null dataset: {non_null_data.shape[0]} rows × {non_null_data.shape[1]} columns")
    
    if save_path:
        non_null_data.to_csv(save_path, index=False)
        print(f"Saved to: {save_path}")
    
    return non_null_data