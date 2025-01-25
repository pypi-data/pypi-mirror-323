"""Tests for module1 (data processing)."""

import pytest
import numpy as np
import pandas as pd
from myframework.module1 import process_data

def test_process_data_numpy():
    """Test processing numpy array data."""
    data = np.random.rand(10, 3)
    result = process_data(data)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (10, 3)

def test_process_data_with_nulls():
    """Test processing data with null values."""
    data = pd.DataFrame({
        'a': [1, 2, None, 4],
        'b': [5, None, 7, 8]
    })
    result = process_data(data)
    assert result.shape == (2, 2)  # After removing nulls
    assert not result.isnull().any().any()

def test_process_data_normalization():
    """Test data normalization."""
    data = pd.DataFrame({
        'a': [1, 2, 3, 4],
        'b': [5, 6, 7, 8]
    })
    result = process_data(data, normalize=True)
    assert np.allclose(result.mean(), 0)  # Normalized data should have mean 0
    assert np.allclose(result.std(), 1)   # Normalized data should have std 1


