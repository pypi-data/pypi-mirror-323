# Cognixis

**Cognixis** is a Python package that provides a set of utilities for building and training regression models using PyTorch. It includes functionality for creating a regression model using a Transformer Encoder, preparing data, and training the model on provided datasets. This package aims to streamline the process of implementing regression tasks with neural networks, focusing on ease of use and flexibility.

## Installation

To install **Cognixis**, use,

```
pip install cognixis
```
## Usage
Once installed, you can use the package to import the Regression class, its components (Encoder, DataGenerator, Trainer), and various utilities for model training and evaluation.
### Importing the Package
```
from cognixis import regression
```
### Creating a Regression Model
You can create a regression model by initializing the Encoder class:


##### Initialize Encoder for regression task
```
input_dim = 10  # Number of input features
output_dim = 1  # Number of output dimensions (single value)
model = regression.Encoder(input_dim, output_dim, d_model:int=32, nhead:int=2, num_layers:int=2, dim_feedforward:int=64, dropout:int=0.1)

```
##### Preparing the Data
You can prepare your dataset using the DataGenerator class, which will split the data into training and testing sets and load it into PyTorch DataLoader objects:

```
# Example numpy arrays for X (features) and y (targets)
import numpy as np

X = np.random.randn(1000, 10)  # 1000 samples, 10 features
y = np.random.randn(1000)      # 1000 target values

# Initialize DataGenerator
data_generator = regression.DataGenerator(X, y, test_size:int=0.2, shuffle:bool=True)

# Access DataLoaders for training and testing
train_loader = data_generator.train_loader
test_loader = data_generator.test_loader

```
### Training the Model
You can use the Trainer class to train your model on the dataset:

```
import torch.optim as optim
import torch.nn as nn

# Define loss function and optimizer
criterion = nn.MSELoss()  # Mean Squared Error Loss for regression
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Initialize the Trainer
trainer = regression.Trainer(model, optimizer, criterion, device="cpu")

# Train the model
train_losses = trainer.train(train_loader, num_epochs=50)

```
### Evaluating the Model
Once the model is trained, you can evaluate it on the test dataset:

```
# Evaluate the model
test_loss = trainer.evaluate(test_loader)
```
### Example: Full Workflow
Here is a complete example that shows how to train and evaluate a model:

```
from cognixis import regression
import numpy as np
import torch.optim as optim
import torch.nn as nn

# Generate random dataset
X = np.random.randn(1000, 10)
y = np.random.randn(1000)

# Initialize DataGenerator
data_generator = regression.DataGenerator(X, y)

# Create a model instance
input_dim = 10
output_dim = 1
model = regression.Encoder(input_dim, output_dim)

# Define loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Initialize Trainer
trainer = regression.Trainer(model, optimizer, criterion, device="cpu")

# Train the model
train_losses = trainer.train(data_generator.train_loader, num_epochs=50)

# Evaluate the model
test_loss = trainer.evaluate(data_generator.test_loader)
```
# Utilities
### Model Summary
You can get a summary of your model using the summary function:

```
from cognixis import summary

# Get model summary
model_summary = summary(model, input_shape=(1, 10), depth=2)  # Example input shape
print(model_summary)
```

Displaying the Source Code of the Train Function
You can also view the source code of the train function:

```
from cognixis import train_code

# Display the train function source code
train_code()

```
License
This project is licensed under the MIT License 



