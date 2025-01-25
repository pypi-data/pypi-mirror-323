"""Pytest configuration file."""

import pytest
import numpy as np
import pandas as pd

@pytest.fixture(scope="session")
def random_seed():
    """Set random seed for reproducibility."""
    np.random.seed(42)
    return 42

@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100),
        'target': np.random.randint(0, 2, 100)
    }) 