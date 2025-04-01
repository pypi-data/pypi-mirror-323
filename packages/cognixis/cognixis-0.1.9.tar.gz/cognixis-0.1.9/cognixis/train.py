import inspect
import torch
from torchinfo import summary as torchinfo_summary
from torch import nn

def train(model, train_loader, test_loader, loss_fn, optimizer, epochs, device):
    """
    Training loop for a PyTorch model.

    Args:
        model (torch.nn.Module): The neural network model to train.
        train_loader (DataLoader): DataLoader for the training dataset.
        test_loader (DataLoader): DataLoader for the test dataset.
        loss_fn (torch.nn.Module): Loss function to optimize.
        optimizer (torch.optim.Optimizer): Optimizer for training.
        epochs (int): Number of training epochs.
        device (torch.device): Device to run the computations (e.g., 'cpu' or 'cuda').
    """
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss, train_correct = 0, 0
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)

            # Forward pass
            y_pred = model(X)
            loss = loss_fn(y_pred, y)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Accumulate loss and correct predictions
            train_loss += loss.item()
            train_correct += (y_pred.argmax(1) == y).sum().item()

        train_accuracy = train_correct / len(train_loader.dataset) * 100

        # Evaluation phase
        model.eval()
        test_loss, test_correct = 0, 0
        with torch.inference_mode():
            for X, y in test_loader:
                X, y = X.to(device), y.to(device)

                # Forward pass
                test_pred = model(X)
                loss = loss_fn(test_pred, y)

                # Accumulate loss and correct predictions
                test_loss += loss.item()
                test_correct += (test_pred.argmax(1) == y).sum().item()

        test_accuracy = test_correct / len(test_loader.dataset) * 100

        # Print metrics for the current epoch
        print(f"Epoch: {epoch + 1}/{epochs} | "
              f"Train Loss: {train_loss:.4f} | Train Accuracy: {train_accuracy:.2f}% | "
              f"Test Loss: {test_loss:.4f} | Test Accuracy: {test_accuracy:.2f}%")


def train_code():
    """Display the source code of the train function."""
    code = inspect.getsource(train)
    print(code)

def summary(model, input_shape, col_names=None, depth=None):
    """
    Wrapper function for torchinfo.summary with default arguments and flexibility.

    Parameters:
    - model (torch.nn.Module): The model to analyze.
    - input_shape (list or tuple): The shape of the input, including batch size.
    - col_names (list, optional): Column names to display. Default is
      ["input_size", "output_size", "num_params", "trainable"].
    - depth (int, optional): Depth of the model to display. Default is None.

    Returns:
    - str: A summary string of the model.
    """
    if col_names is None:
        col_names = ["input_size", "output_size", "num_params", "trainable"]
    
    return torchinfo_summary(
        model=model,
        input_size=tuple(input_shape),
        col_names=col_names,
        depth=depth,
    )


class Embedding(nn.Module):
    def __init__(self, in_channels, embedding_dim, patch_size, height, width):
        if width % patch_size != 0 or height % patch_size != 0:
            raise ValueError("Width and height must be divisible by patch_size.")
        super().__init__()
        self.height = height
        self.width = width
        self.Embedding = nn.Conv2d(
            in_channels, embedding_dim, kernel_size=patch_size, stride=patch_size, padding=0
        )
        self.flatten = nn.Flatten(start_dim=2)
        self.class_embedding = nn.Parameter(torch.randn(1, 1, embedding_dim))
        self.positional_embedding = nn.Parameter(
            torch.randn(1, (height // patch_size) * (width // patch_size) + 1, embedding_dim)
        )

    def forward(self, x):
        batch_size, channels, height, width = x.shape
        if height != self.height or width != self.width:
            raise ValueError("Input height and width must match the initialized height and width.")
        z = self.Embedding(x)
        z = self.flatten(z)
        z = z.permute(0, 2, 1)
        z = torch.cat((self.class_embedding.expand(batch_size, -1, -1), z), dim=1)
        z += self.positional_embedding.expand(batch_size, -1, -1)
        return z

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

class Regression:
    class Encoder(nn.Module):
        def __init__(self, input_dim, output_dim, d_model=32, nhead=2, num_layers=2, dim_feedforward=64, dropout=0.1):
            super().__init__()
            self.input_projection = nn.Linear(input_dim, d_model)
            self.pos_encoder = nn.Parameter(torch.randn(1, input_dim, d_model))

            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=dim_feedforward,
                dropout=dropout,
                batch_first=True
            )
            self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            self.output_projection = nn.Linear(d_model * input_dim, output_dim)

        def forward(self, x):
            x = self.input_projection(x.unsqueeze(1))  # Add sequence dimension
            x = x + self.pos_encoder
            x = self.transformer_encoder(x)
            x = x.view(x.size(0), -1)  # Flatten for the final projection
            return self.output_projection(x).squeeze(-1)

    class DataGenerator:
        def __init__(self, X, y, test_size=0.2, batch_size=32, shuffle=True):
            """
            Splits X and y into train and test sets, converts them into PyTorch DataLoaders.

            Args:
                X (numpy.ndarray): Input features, shape (num_samples, num_features).
                y (numpy.ndarray): Targets, shape (num_samples,).
                test_size (float): Fraction of the dataset to be used as the test set.
                batch_size (int): Batch size for the DataLoaders.
                shuffle (bool): Whether to shuffle the dataset.
            """
            self.X = np.asarray(X, dtype=np.float32)
            self.y = np.asarray(y, dtype=np.float32)

            # Split the data
            n_test = int(len(y) * test_size)
            indices = np.random.permutation(len(y))

            test_idx = indices[:n_test]
            train_idx = indices[n_test:]

            X_train, X_test = self.X[train_idx], self.X[test_idx]
            y_train, y_test = self.y[train_idx], self.y[test_idx]

            # Convert to PyTorch tensors
            self.train_dataset = TensorDataset(torch.tensor(X_train), torch.tensor(y_train))
            self.test_dataset = TensorDataset(torch.tensor(X_test), torch.tensor(y_test))

            # Create DataLoaders
            self.train_loader = DataLoader(self.train_dataset, batch_size=batch_size, shuffle=shuffle)
            self.test_loader = DataLoader(self.test_dataset, batch_size=batch_size, shuffle=False)

    class Trainer:
        def __init__(self, model, optimizer, criterion, device="cpu"):
            """
            Trainer for regression tasks using PyTorch.

            Args:
                model (nn.Module): PyTorch model to train.
                optimizer (torch.optim.Optimizer): Optimizer for model parameters.
                criterion (nn.Module): Loss function (e.g., nn.MSELoss).
                device (str): Device to run the model on ('cpu' or 'cuda').
            """
            self.model = model.to(device)
            self.optimizer = optimizer
            self.criterion = criterion
            self.device = device

        def train(self, train_loader, num_epochs=50):
            """
            Train the model.

            Args:
                train_loader (DataLoader): DataLoader for training data.
                num_epochs (int): Number of epochs to train.

            Returns:
                list: Training loss per epoch.
            """
            train_losses = []

            for epoch in range(num_epochs):
                self.model.train()
                total_loss = 0

                for batch_X, batch_y in train_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)

                    self.optimizer.zero_grad()
                    outputs = self.model(batch_X)
                    loss = self.criterion(outputs, batch_y)
                    loss.backward()
                    self.optimizer.step()

                    total_loss += loss.item()

                avg_loss = total_loss / len(train_loader)
                train_losses.append(avg_loss)

                if (epoch + 1) % 10 == 0:
                    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")

            return train_losses

        def evaluate(self, test_loader):
            """
            Evaluate the model on test data.

            Args:
                test_loader (DataLoader): DataLoader for testing data.

            Returns:
                float: Average test loss.
            """
            self.model.eval()
            total_loss = 0

            with torch.no_grad():
                for batch_X, batch_y in test_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = self.model(batch_X)
                    loss = self.criterion(outputs, batch_y)
                    total_loss += loss.item()

            avg_loss = total_loss / len(test_loader)
            print(f"Test Loss: {avg_loss:.4f}")
            return avg_loss
