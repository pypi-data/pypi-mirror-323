# MyFramework Documentation

## Overview

MyFramework is a Python framework designed to simplify machine learning workflows. It provides tools for data processing, model training, and evaluation.

## Installation

```bash
pip install myframework
```

## Core Modules

### module1 (Data Processing)

The `module1` module provides functions for data preprocessing:

```python
from myframework.module1 import process_data

# Process your data
processed_data = process_data(your_data, remove_nulls=True, normalize=True)
```

### module2 (ML Utilities)

The `module2` module contains machine learning utilities:

```python
from myframework.module2 import train_model, evaluate_model

# Train a model
model = train_model(X_train, y_train)

# Evaluate the model
metrics = evaluate_model(model, X_test, y_test)
```

### Utils

Utility functions for common operations:

```python
from myframework.utils import validate_input, save_model, load_model

# Validate your data
validate_input(data, requirements={'no_nulls': True, 'min_rows': 10})

# Save and load models
save_model(model, 'model.pkl')
loaded_model = load_model('model.pkl')
```

## Contributing

We welcome contributions! Please see our contributing guidelines for more information. 