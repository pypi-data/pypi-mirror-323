"""Data processing module for handling various data transformations."""

import numpy as np
import pandas as pd

def process_data(data, **kwargs):
    print("process data is functioning properly")
    """
    Process input data with basic transformations.
    
    Args:
        data: Input data (numpy array or pandas DataFrame)
        **kwargs: Additional processing parameters
        
    Returns:
        Processed data
    """
    if isinstance(data, np.ndarray):
        data = pd.DataFrame(data)
    
    # Example processing steps
    if kwargs.get('remove_nulls', True):
        data = data.dropna()
    
    if kwargs.get('normalize', True):
        data = (data - data.mean()) / data.std()
    
    return data 