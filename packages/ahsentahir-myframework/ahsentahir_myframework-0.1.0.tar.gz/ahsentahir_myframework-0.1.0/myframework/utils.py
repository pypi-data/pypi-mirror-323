"""Utility functions for data validation and common operations."""

import numpy as np
import pandas as pd
import torch

def validate_input(data, requirements=None):
    print("validate input is working")
    """
    Validate input data against requirements.
    
    Args:
        data: Input data to validate
        requirements: Dictionary of validation requirements
        
    Returns:
        bool: True if valid, raises ValueError if invalid
    """
    if requirements is None:
        requirements = {'no_nulls': True, 'min_rows': 1}
    
    if isinstance(data, np.ndarray):
        data = pd.DataFrame(data)
    
    if requirements.get('no_nulls') and data.isnull().any().any():
        raise ValueError("Data contains null values")
    
    if len(data) < requirements.get('min_rows', 1):
        raise ValueError(f"Data must have at least {requirements['min_rows']} rows")
    
    return True

def save_model(model, path):
    """
    Save PyTorch model to disk.
    
    Args:
        model: Trained PyTorch model
        path: Path to save the model (should end with .pt)
    """
    if not path.endswith('.pt'):
        path = path + '.pt'
    torch.save(model.state_dict(), path)

def load_model(path, model_class=None, **model_kwargs):
    print("load model is working")
    """
    Load PyTorch model from disk.
    
    Args:
        path: Path to the saved model
        model_class: PyTorch model class to instantiate
        **model_kwargs: Arguments to pass to model class constructor
        
    Returns:
        Loaded PyTorch model
    """
    if model_class is None:
        from .module2 import BasicNet
        model_class = BasicNet
    
    model = model_class(**model_kwargs)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model

def prepare_data_for_training(data, target_column=None):
    print("prepare data for training is working")
    """
    Prepare data for model training.
    
    Args:
        data: Input DataFrame
        target_column: Name of the target column
        
    Returns:
        X: Features array
        y: Target array (if target_column provided)
    """
    if target_column is not None:
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")
        y = data[target_column].values
        X = data.drop(columns=[target_column]).values
        return X, y
    return data.values 