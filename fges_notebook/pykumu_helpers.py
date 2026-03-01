"""
PyKumu Helper Functions
=======================

Helper functions for causal analysis matching Kumu's R implementation.
This module provides utilities for data loading, configuration, and validation.

Author: Migrated from Kumu R package
Date: February 2026
"""

import pandas as pd
import numpy as np
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
