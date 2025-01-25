"""
MyFramework - A Python Framework for ML Automation

This framework provides tools and utilities for automating machine learning workflows.
"""

from .module1 import process_data
from .module2 import train_model, evaluate_model, create_basic_model
from .utils import validate_input, save_model, load_model, prepare_data_for_training

__version__ = "0.1.0"
__all__ = [
    "process_data",
    "train_model",
    "evaluate_model",
    "create_basic_model",
    "validate_input",
    "save_model",
    "load_model",
    "prepare_data_for_training"
] 