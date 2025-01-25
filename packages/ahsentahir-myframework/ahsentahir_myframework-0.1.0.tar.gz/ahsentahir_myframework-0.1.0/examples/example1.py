"""Example script demonstrating the usage of MyFramework with PyTorch."""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from myframework.module1 import process_data
from myframework.module2 import train_model, evaluate_model
from myframework.utils import validate_input, save_model

# Create sample data
np.random.seed(42)
n_samples = 1000
n_features = 5

# Generate more complex data for deep learning
X = np.random.randn(n_samples, n_features)
# Create a non-linear target
y = ((X[:, 0]**2 + X[:, 1]**2 + X[:, 2] * X[:, 3]) > 1).astype(float)

# Convert to DataFrame
data = pd.DataFrame(X, columns=[f'feature_{i+1}' for i in range(n_features)])

# Validate input data
validate_input(data, requirements={'no_nulls': True, 'min_rows': 100})

# Process data
processed_data = process_data(data, normalize=True)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    processed_data, y, test_size=0.2, random_state=42
)

# Train model with specific parameters
model, history = train_model(
    X_train.values, y_train,
    epochs=20,
    batch_size=32,
    learning_rate=0.001,
    validation_split=0.2
)

# Print final training metrics
print("\nFinal Training Metrics:")
print(f"Training Loss: {history['train_loss'][-1]:.4f}")
print(f"Training Accuracy: {history['train_acc'][-1]:.4f}")
print(f"Validation Loss: {history['val_loss'][-1]:.4f}")
print(f"Validation Accuracy: {history['val_acc'][-1]:.4f}")

# Evaluate model on test set
metrics = evaluate_model(model, X_test.values, y_test)
print("\nTest Set Performance:")
for metric, value in metrics.items():
    print(f"{metric}: {value:.3f}")

# Save model
save_model(model, 'example_model.pt') 