"""
**Learn the Basics** >
`Tensors <tensor_tutorial.html>`_ > 
`Datasets & DataLoaders <dataquickstart_tutorial.html>`_ >
`Transforms <transforms_tutorial.html>`_ >
`Build Model <buildmodel_tutorial.html>`_ >
`Autograd <autograd_tutorial.html>`_ >
`Optimization <optimization_tutorial.html>`_ >
`Save & Load Model <saveloadrun_tutorial.html>`_

Learn the Basics
===================

Authors: 
`Suraj Subramanian <https://github.com/suraj813>`_,
`Seth Juarez <https://github.com/sethjuarez/>`_, 
`Cassie Breviu <https://github.com/cassieview/>`_, 
`Dmitry Soshnikov <https://soshnikov.com/>`_, 
`Ari Bornstein <https://github.com/aribornstein/>`_ 

A basic machine learning workflow involves working with data, creating models, optimizing model 
parameters, and saving the trained models. This tutorial introduces you to the complete ML workflow 
as implemented in PyTorch, with links to learn more about of these concepts.

We'll use the FashionMNIST dataset to train a neural network that predicts if an input image belongs 
to one of the following classes: T-shirt/top, Trouser, Pullover, Dress, Coat, Sandal, Shirt, Sneaker, 
Bag, or Ankle boot. 

This tutorial assumes a basic familiarity with Python and Deep Learning concepts.

Running the Tutorial Code
------------------
You can run this tutorial in a few ways:

- **In the cloud**: This is the easiest way to get started! Each section has a Colab link at the top, which opens a notebook with the code in a fully-hosted environment. Pro tip: Use Colab with a GPU runtime to speed up operations *Runtime > Change runtime type > GPU*
- **Locally**: This option requires you to setup PyTorch and TorchVision first on your local machine (`installation instructions <https://pytorch.org/get-started/locally/>`_). Download the notebook or copy the code into your favorite IDE.


How to Use this Guide
-----------------
This page contains an overview of the code used at each step of the tutorial. If you're familiar with 
other deep learning frameworks, this is a quick way to get acquainted with PyTorch's API. 

If this is your first time, head right into our step-by-step guide:

.. include:: /beginner_source/quickstart/qs_toc.txt

.. toctree::
   :hidden:

   /beginner/quickstart/tensor_tutorial
   /beginner/quickstart/dataquickstart_tutorial
   /beginner/quickstart/transforms_tutorial
   /beginner/quickstart/buildmodel_tutorial
   /beginner/quickstart/autograd_tutorial
   /beginner/quickstart/optimization_tutorial
   /beginner/quickstart/saveloadrun_tutorial



--------------


Working with data
-----------------
PyTorch has two data primitives to work with data: ``torch.utils.data.DataLoader`` and ``torch.utils.data.Dataset``.
``Dataset`` stores the samples and their corresponding labels, and ``DataLoader`` wraps an iterable around
the ``Dataset``.

"""

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
import matplotlib.pyplot as plt

######################################################################
# The ``torchvision.datasets`` module contains ``Dataset`` objects for many real-world vision data like 
# CIFAR, COCO (`full list here <https://pytorch.org/docs/stable/torchvision/datasets.html>`_). In this tutorial, we
# use the FashionMNIST dataset. Every TorchVision ``Dataset`` includes two arguments: ``transform`` and
# ``target_transform`` to modify the samples and labels respectively.

classes = [
    "T-shirt/top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle boot",
]

# Download training data from open datasets.
training_data = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
    target_transform=Lambda(lambda y: torch.zeros(10, dtype=torch.float).scatter_(0, torch.tensor(y), value=1))
)

# Download test data from open datasets.
test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor(),
    target_transform=Lambda(lambda y: torch.zeros(10, dtype=torch.float).scatter_(0, torch.tensor(y), value=1))
)

######################################################################
# We pass the ``Dataset`` as an argument to ``DataLoader``. This wraps an iterable over our dataset, and supports
# automatic batching, sampling, shuffling and multiprocess data loading. Here we define a batch size of 64, i.e. each element 
# in the dataloader iterable will return a batch of 64 features and labels.

batch_size = 64

# Create data loaders.
train_dataloader = DataLoader(training_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

for X, y in test_dataloader:
    print("Shape of X [N, C, H, W]: ", X.shape)
    print("Shape of y: ", y.shape)
    break

######################################################################
# --------------
#

################################
# Creating Models
# ------------------
# To define a neural network in PyTorch, we create a class that inherits 
# from `nn.Module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html)>`_. We define the layers of the network
# in the ``__init__`` function and specify how data will pass through the network in the ``forward`` function. To accelerate 
# operations in the NN, we move it to the GPU if available.

# Get cpu or gpu device for training.
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using {} device".format(device))

# Define model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.softmax = nn.Softmax(dim=1)
        self.nn_layers = nn.Sequential(
                            nn.Linear(28 * 28, 512),
                            nn.ReLU(),
                            nn.Linear(512, 512),
                            nn.ReLU(),
                            nn.Linear(512, 10)
                        )
    def forward(self, x):
        x = self.flatten(x)
        x = self.nn_layers(x)
        return self.softmax(x)

model = NeuralNetwork().to(device)
print(model)

######################################################################
# Read more about `building neural networks in PyTorch <buildmodel_tutorial.html>`_.
#


######################################################################
# --------------
#

#####################################################################
# Training the Model 
# ----------------------------------------
# To train a model, we need a `loss function <https://pytorch.org/docs/stable/nn.html#loss-functions>`_
# and an `optimizer <https://pytorch.org/docs/stable/optim.html>`_. 

loss_fn = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

####################################################################### 
# In a single training loop, the model makes predictions on the training dataset (fed to it in batches), and 
# backpropagates the prediction error to adjust the model's parameters. 

def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        
        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)
        
        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

##############################################################################
# We also check the model's performance against the test dataset to ensure it is learning.

def test(dataloader, model):
    size = len(dataloader.dataset)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y.argmax(1)).type(torch.float).sum().item()
    test_loss /= size
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

##############################################################################
# The training process is conducted over several iterations (*epochs*). During each epoch, the model learns 
# parameters to make better predictions. We print the model's accuracy and loss at each epoch; we'd like to see the
# accuracy increase and the loss decrease with every epoch.

epochs = 5
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model)
print("Done!")

######################################################################
# Read more about `Training your model <optimization_tutorial.html>`_.
#

######################################################################
# --------------
#

######################################################################
# Saving Models
# -------------
# A common way to save a model is to serialize the internal state dictionary (containing the model parameters).

torch.save(model.state_dict(), "model.pth")
print("Saved PyTorch Model State to model.pth")


######################################################################
# --------------
#


######################################################################
# Loading Models
# ----------------------------
#
# The process for loading a model includes re-creating the model structure and loading
# the state dictionary into it. 

model = NeuralNetwork()
model.load_state_dict(torch.load("model.pth"))

#############################################################
# This model can now be used to make predictions.

model.eval()
x, y = test_data[0][0], test_data[0][1]
with torch.no_grad():
    pred = model(x)
    predicted, actual = classes[pred[0].argmax(0)], classes[y.argmax(0)]
    print(f'Predicted: "{predicted}", Actual: "{actual}"')
