"""Machine learning utilities module with basic deep learning functionality using PyTorch."""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

class BasicNet(nn.Module):
    """Basic neural network architecture."""
    
    def __init__(self, input_size, hidden_size=64, num_classes=2):
        """
        Initialize the network.
        
        Args:
            input_size: Number of input features
            hidden_size: Size of hidden layer (default: 64)
            num_classes: Number of output classes (default: 2)
        """
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, num_classes)
        )
        
        # Add sigmoid for binary classification, otherwise use softmax
        self.output_activation = nn.Sigmoid() if num_classes == 1 else nn.Softmax(dim=1)
    
    def forward(self, x):
        """Forward pass."""
        x = self.network(x)
        return self.output_activation(x)

def create_basic_model(input_shape, num_classes=2):
    print("create basic model is working")
    """
    Create a basic neural network model.
    
    Args:
        input_shape: Shape of input features
        num_classes: Number of output classes (default: 2)
        
    Returns:
        PyTorch model
    """
    input_size = input_shape[0] if isinstance(input_shape, tuple) else input_shape
    # For binary classification, use 1 output
    output_size = 1 if num_classes == 2 else num_classes
    return BasicNet(input_size, num_classes=output_size)

def train_model(X, y, model=None, **kwargs):
    print("train model function is working")
    """
    Train a deep learning model.
    
    Args:
        X: Features (numpy array)
        y: Target variable
        model: Pre-initialized PyTorch model (optional)
        **kwargs: Additional training parameters
            - epochs: Number of training epochs (default: 10)
            - batch_size: Batch size for training (default: 32)
            - learning_rate: Learning rate (default: 0.001)
            - validation_split: Fraction of data for validation (default: 0.2)
        
    Returns:
        Trained model and training history
    """
    # Convert data to PyTorch tensors
    X = torch.FloatTensor(X)
    y = torch.FloatTensor(y)
    
    # Create model if not provided
    if model is None:
        model = create_basic_model(X.shape[1])
    
    # Extract training parameters
    epochs = kwargs.get('epochs', 10)
    batch_size = kwargs.get('batch_size', 32)
    learning_rate = kwargs.get('learning_rate', 0.001)
    validation_split = kwargs.get('validation_split', 0.2)
    
    # Create data loaders
    dataset = TensorDataset(X, y.reshape(-1, 1))
    train_size = int((1 - validation_split) * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    # Define loss function and optimizer
    criterion = nn.BCELoss() if model.network[-1].out_features == 1 else nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Training history
    history = {
        'train_loss': [],
        'val_loss': [],
        'train_acc': [],
        'val_acc': []
    }
    
    # Training loop
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            predicted = (outputs > 0.5).float()
            train_total += batch_y.size(0)
            train_correct += (predicted == batch_y).sum().item()
        
        # Validation
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item()
                predicted = (outputs > 0.5).float()
                val_total += batch_y.size(0)
                val_correct += (predicted == batch_y).sum().item()
        
        # Record history
        history['train_loss'].append(train_loss / len(train_loader))
        history['val_loss'].append(val_loss / len(val_loader))
        history['train_acc'].append(train_correct / train_total)
        history['val_acc'].append(val_correct / val_total)
        
        print(f'Epoch {epoch+1}/{epochs}:')
        print(f'Train Loss: {history["train_loss"][-1]:.4f}, Train Acc: {history["train_acc"][-1]:.4f}')
        print(f'Val Loss: {history["val_loss"][-1]:.4f}, Val Acc: {history["val_acc"][-1]:.4f}')
    
    return model, history

def evaluate_model(model, X, y):
    print("evaluate model is working")
    """
    Evaluate model performance.
    
    Args:
        model: Trained PyTorch model
        X: Test features
        y: Test target
        
    Returns:
        Dictionary of evaluation metrics
    """
    model.eval()
    X = torch.FloatTensor(X)
    y = torch.FloatTensor(y)
    
    with torch.no_grad():
        outputs = model(X)
        predicted = (outputs > 0.5).float().numpy().ravel()
    
    # Calculate metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    
    return {
        'accuracy': accuracy_score(y, predicted),
        'precision': precision_score(y, predicted, average='weighted'),
        'recall': recall_score(y, predicted, average='weighted')
    } 