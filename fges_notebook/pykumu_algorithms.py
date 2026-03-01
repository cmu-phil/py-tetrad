"""
PyKumu Algorithm Execution Functions
=====================================

Algorithm wrappers for BOSS and FGES causal discovery matching Kumu's R implementation.
This module provides execution functions with output suppression and result extraction.

Author: Migrated from Kumu R package
Date: February 2026
"""

import pandas as pd
import time
import os
import io
import contextlib
from typing import Dict, Optional
import pytetrad.tools.TetradSearch as ts

# Import Java classes for System.out redirection
import jpype
import jpype.imports
try:
    import java.lang as lang
    import java.io as jio
except:
    pass  # Will be available after JVM starts


class SuppressJavaOutput:
    """Context manager to suppress Java System.out and System.err output."""
    
    def __enter__(self):
        try:
            # Save original streams
            self.original_out = lang.System.out
            self.original_err = lang.System.err
            
            # Create a ByteArrayOutputStream (discards data) and wrap in PrintStream
            byte_array_stream = jio.ByteArrayOutputStream()
            null_print_stream = jio.PrintStream(byte_array_stream)
            
            # Redirect Java streams to null
            lang.System.setOut(null_print_stream)
            lang.System.setErr(null_print_stream)
        except Exception as e:
            # If Java classes not available, do nothing
            pass
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # Restore original streams
            lang.System.setOut(self.original_out)
            lang.System.setErr(self.original_err)
        except:
            pass
        return False


def run_boss(search: ts.TetradSearch,
             num_starts: int = 1,
             use_bes: bool = False,
             time_lag: int = 0,
             use_data_order: bool = True,
             output_cpdag: bool = True,
             suppress_output: bool = True) -> Dict:
    """
    Execute BOSS causal search with bootstrapping.
    
    Matches R function: tetrad() with algorithm_boss()
    
    Parameters
    ----------
    search : TetradSearch
        Configured TetradSearch object (must have score and bootstrapping set)
    num_starts : int
        Number of random restarts
    use_bes : bool
        Use BES (Backward Equivalence Search) from GES
    time_lag : int
        Time lag for time-series data (0 = no lag)
    use_data_order : bool
        Use data variable order for first permutation
    output_cpdag : bool
        Output CPDAG (Completed Partially Directed Acyclic Graph) format
    suppress_output : bool
        Suppress Java bootstrap iteration output
        
    Returns
    -------
    dict
        Execution summary with keys:
        - 'elapsed_time': Execution time in seconds
        - 'n_nodes': Number of nodes in graph
        - 'n_edges': Number of edges in graph
        - 'search': Reference to search object for further analysis
        
    Example
    -------
    >>> search = configure_boss_search(data)
    >>> results = run_boss(search)
    >>> print(f"BOSS found {results['n_edges']} edges in {results['elapsed_time']:.0f}s")
    """
    print("Running BOSS with bootstrapping...")
    start_time = time.time()
    
    # Execute with optional output suppression
    if suppress_output:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            search.run_boss(
                num_starts=num_starts,
                use_bes=use_bes,
                time_lag=time_lag,
                use_data_order=use_data_order,
                output_cpdag=output_cpdag
            )
    else:
        search.run_boss(
            num_starts=num_starts,
            use_bes=use_bes,
            time_lag=time_lag,
            use_data_order=use_data_order,
            output_cpdag=output_cpdag
        )
    
    elapsed_time = time.time() - start_time
    
    # Get graph summary
    graph = search.get_java()
    n_nodes = graph.getNumNodes()
    n_edges = graph.getNumEdges()
    
    print(f"✓ BOSS completed in {elapsed_time:.0f}s ({elapsed_time/60:.1f} min)")
    print(f"  Nodes: {n_nodes}, Edges: {n_edges}")
    
    return {
        'elapsed_time': elapsed_time,
        'n_nodes': n_nodes,
        'n_edges': n_edges,
        'search': search
    }


def run_fges(search: ts.TetradSearch,
             max_degree: int = 1000,
             faithfulness_assumed: bool = True,
             symmetric_first_step: bool = True,
             parallelized: bool = False,
             suppress_output: bool = True) -> Dict:
    """
    Execute FGES causal search with bootstrapping.
    
    Matches R function: tetrad() with algorithm_fges()
    
    Parameters
    ----------
    search : TetradSearch
        Configured TetradSearch object (must have score and bootstrapping set)
    max_degree : int
        Maximum number of edges per node
    faithfulness_assumed : bool
        Assume faithfulness condition
    symmetric_first_step : bool
        Use symmetric scoring in first step
    parallelized : bool
        Use parallel processing
    suppress_output : bool
        Suppress Java bootstrap iteration output
        
    Returns
    -------
    dict
        Execution summary (same format as run_boss)
        
    Example
    -------
    >>> search = configure_fges_search(data)
    >>> results = run_fges(search, max_degree=1000)
    >>> print(f"FGES found {results['n_edges']} edges in {results['elapsed_time']:.0f}s")
    """
    print("Running FGES with bootstrapping...")
    start_time = time.time()
    
    # Execute with optional output suppression
    if suppress_output:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            search.run_fges(
                max_degree=max_degree,
                faithfulness_assumed=faithfulness_assumed,
                symmetric_first_step=symmetric_first_step,
                parallelized=parallelized
            )
    else:
        search.run_fges(
            max_degree=max_degree,
            faithfulness_assumed=faithfulness_assumed,
            symmetric_first_step=symmetric_first_step,
            parallelized=parallelized
        )
    
    elapsed_time = time.time() - start_time
    
    # Get graph summary
    graph = search.get_java()
    n_nodes = graph.getNumNodes()
    n_edges = graph.getNumEdges()
    
    print(f"✓ FGES completed in {elapsed_time:.0f}s ({elapsed_time/60:.1f} min)")
    print(f"  Nodes: {n_nodes}, Edges: {n_edges}")
    
    return {
        'elapsed_time': elapsed_time,
        'n_nodes': n_nodes,
        'n_edges': n_edges,
        'search': search
    }


def extract_results(search: ts.TetradSearch, 
                   output_dir: Optional[str] = None,
                   save_files: bool = True) -> Dict:
    """
    Extract and optionally save causal search results.
    
    Matches R output: Adjacency matrix + edge list + graph string + JSON
    
    Parameters
    ----------
    search : TetradSearch
        Completed TetradSearch object (after run_boss or run_fges)
    output_dir : str, optional
        Directory to save results. If None, uses current directory
    save_files : bool
        Whether to save files to disk
        
    Returns
    -------
    dict
        Results dictionary with keys:
        - 'graph': Java graph object
        - 'graph_string': Text representation of graph
        - 'graph_json': JSON representation of graph
        - 'adjacency_matrix': DataFrame with adjacency matrix
        - 'edges': DataFrame with edge list
        - 'n_nodes': Number of nodes
        - 'n_edges': Number of edges
        
    Example
    -------
    >>> results = extract_results(search, output_dir="boss_results")
    >>> print(f"Saved {len(results['edges'])} edges to {output_dir}")
    """
    # Get graph objects
    graph = search.get_java()
    graph_string = search.get_string()
    graph_json = search.get_json()
    graph_xml = search.get_xml()  # XML format for Tetrad GUI
    adjacency_matrix = search.get_graph_to_matrix()
    
    # Extract edge list
    edges = []
    for i, var1 in enumerate(adjacency_matrix.columns):
        for j, var2 in enumerate(adjacency_matrix.columns):
            if i < j:
                endpoint1 = adjacency_matrix.iloc[i, j]
                endpoint2 = adjacency_matrix.iloc[j, i]
                if endpoint1 != 0 or endpoint2 != 0:
                    edges.append({
                        'From': var1,
                        'To': var2,
                        'Endpoint_From': int(endpoint1),
                        'Endpoint_To': int(endpoint2)
                    })
    
    edges_df = pd.DataFrame(edges)
    
    # Save files if requested
    if save_files and output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        adjacency_matrix.to_csv(f"{output_dir}/adjacency_matrix.csv")
        edges_df.to_csv(f"{output_dir}/edge_list.csv", index=False)
        
        with open(f"{output_dir}/graph_string.txt", "w") as f:
            f.write(str(graph_string))
        
        with open(f"{output_dir}/graph.json", "w") as f:
            f.write(str(graph_json))
        
        with open(f"{output_dir}/graph.xml", "w") as f:
            f.write(str(graph_xml))
        
        print(f"✓ Results saved to {output_dir}/")
        print(f"  - adjacency_matrix.csv ({adjacency_matrix.shape[0]}×{adjacency_matrix.shape[1]})")
        print(f"  - edge_list.csv ({len(edges_df)} edges)")
        print(f"  - graph_string.txt")
        print(f"  - graph.json")
        print(f"  - graph.xml (for Tetrad GUI)")
    
    return {
        'graph': graph,
        'graph_string': graph_string,
        'graph_json': graph_json,
        'graph_xml': graph_xml,
        'adjacency_matrix': adjacency_matrix,
        'edges': edges_df,
        'n_nodes': graph.getNumNodes(),
        'n_edges': len(edges_df)
    }


def run_boss_analysis(data: pd.DataFrame,
                     knowledge_file: Optional[str] = None,
                     output_dir: str = "boss_results",
                     suppress_output: bool = True,
                     **config_params) -> Dict:
    """
    Complete BOSS analysis workflow: configure → run → extract results.
    
    This is a convenience function that combines configure_boss_search(),
    run_boss(), and extract_results() in one call.
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataset for causal analysis
    knowledge_file : str, optional
        Path to knowledge constraints file
    output_dir : str
        Directory to save results
    suppress_output : bool
        Suppress all output including bootstrap counts (default: True)
    **config_params
        Additional configuration parameters passed to configure_boss_search():
        - penalty_discount (float): SEM-BIC penalty (default: 2)
        - n_bootstrap (int): Bootstrap iterations (default: 1000)
        - seed (int): Random seed (default: 32)
        - time_lag (int): Time lag (default: 0)
        - verbose (bool): Print output (default: False)
        
    Returns
    -------
    dict
        Combined results from run_boss() and extract_results()
        
    Example
    -------
    >>> # One-line complete analysis
    >>> results = run_boss_analysis(data, 
    ...                             knowledge_file="knowledge.txt",
    ...                             output_dir="boss_results",
    ...                             n_bootstrap=1000)
    """
    from pykumu_helpers import configure_boss_search
    import sys
    
    if suppress_output:
        # Suppress all output including Java stdout
        with SuppressJavaOutput(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            # Configure
            search = configure_boss_search(data, knowledge_file=knowledge_file, **config_params)
            
            # Run
            exec_results = run_boss(search, suppress_output=True)
            
            # Extract and save
            file_results = extract_results(search, output_dir=output_dir, save_files=True)
        
        # Print only the final summary
        print(f"BOSS completed: {exec_results['n_nodes']} nodes, {exec_results['n_edges']} edges")
        print(f"Elapsed: {exec_results['elapsed_time']:.1f}s")
    else:
        # Configure
        search = configure_boss_search(data, knowledge_file=knowledge_file, **config_params)
        
        # Run
        exec_results = run_boss(search, suppress_output=False)
        
        # Extract and save
        file_results = extract_results(search, output_dir=output_dir, save_files=True)
    
    # Combine results
    return {**exec_results, **file_results}


def run_fges_analysis(data: pd.DataFrame,
                     knowledge_file: Optional[str] = None,
                     output_dir: str = "fges_results",
                     suppress_output: bool = True,
                     **config_params) -> Dict:
    """
    Complete FGES analysis workflow: configure → run → extract results.
    
    This is a convenience function that combines configure_fges_search(),
    run_fges(), and extract_results() in one call.
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataset for causal analysis
    knowledge_file : str, optional
        Path to knowledge constraints file
    output_dir : str
        Directory to save results
    suppress_output : bool
        Suppress all output including bootstrap counts (default: True)
    **config_params
        Additional configuration parameters passed to configure_fges_search():
        - penalty_discount (float): SEM-BIC penalty (default: 2)
        - n_bootstrap (int): Bootstrap iterations (default: 500)
        - seed (int): Random seed (default: 32)
        - time_lag (int): Time lag (default: 0)
        - verbose (bool): Print output (default: False)
        
    Returns
    -------
    dict
        Combined results from run_fges() and extract_results()
        
    Example
    -------
    >>> # One-line complete analysis
    >>> results = run_fges_analysis(data, 
    ...                             knowledge_file="knowledge.txt",
    ...                             output_dir="fges_results",
    ...                             n_bootstrap=500)
    """
    from pykumu_helpers import configure_fges_search
    import sys
    
    if suppress_output:
        # Suppress all output including Java stdout
        with SuppressJavaOutput(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            # Configure
            search = configure_fges_search(data, knowledge_file=knowledge_file, **config_params)
            
            # Run
            exec_results = run_fges(search, suppress_output=True)
            
            # Extract and save
            file_results = extract_results(search, output_dir=output_dir, save_files=True)
        
        # Print only the final summary
        print(f"FGES completed: {exec_results['n_nodes']} nodes, {exec_results['n_edges']} edges")
        print(f"Elapsed: {exec_results['elapsed_time']:.1f}s")
    else:
        # Configure
        search = configure_fges_search(data, knowledge_file=knowledge_file, **config_params)
        
        # Run
        exec_results = run_fges(search, suppress_output=False)
        
        # Extract and save
        file_results = extract_results(search, output_dir=output_dir, save_files=True)
    
    # Combine results
    return {**exec_results, **file_results}
