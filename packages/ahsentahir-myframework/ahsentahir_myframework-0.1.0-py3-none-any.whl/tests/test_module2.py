"""Tests for module2 (ML utilities)."""

import pytest
import numpy as np
import torch
from sklearn.datasets import make_classification
from myframework.module2 import train_model, evaluate_model, create_basic_model

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    X, y = make_classification(
        n_samples=100,
        n_features=4,
        n_informative=2,
        n_redundant=0,
        random_state=42
    )
    return X, y

def test_train_model(sample_data):
    """Test model training functionality."""
    X, y = sample_data
    model, history = train_model(X, y)
    
    # Test that we got a PyTorch model
    assert isinstance(model, torch.nn.Module)
    # Test that history contains expected metrics
    assert all(key in history for key in ['train_loss', 'val_loss', 'train_acc', 'val_acc'])
    # Test that metrics are within valid ranges
    assert all(0 <= loss <= 10 for loss in history['train_loss'])
    assert all(0 <= acc <= 1 for acc in history['train_acc'])

def test_evaluate_model(sample_data):
    """Test model evaluation functionality."""
    X, y = sample_data
    model, _ = train_model(X, y)
    metrics = evaluate_model(model, X, y)
    
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert all(0 <= v <= 1 for v in metrics.values())
    
