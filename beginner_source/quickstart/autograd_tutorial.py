"""
Automatic Differentiation with AutoGrad
=======================================

When training neural networks, the most frequently used algorithm is
**back propagation**. In this algorithm, parameters (model weights) are
adjusted according to the **gradient** of the loss function with respect
to the given parameter.

To compute those gradients, PyTorch has a built-in mechanism called
**AutoGrad**. It supports automatic computation of gradient for any
computational graph.

Consider the simplest one-layer neural network, with input ``x``,
parameters ``w`` and ``b``, and some loss function. It can be defined in
PyTorch in the following manner:
"""

import torch
x = torch.ones(5) # input tensor
y = torch.zeros(3) # expected output
w = torch.randn(5,3,requires_grad=True)
b = torch.randn(3,requires_grad=True)
z = torch.matmul(x,w)+b
loss = torch.nn.functional.binary_cross_entropy_with_logits(z,y)


######################################################################
# Tensors, Functions and Computational graph
# ------------------------------------------
#
# This code defines the following **computational graph**:
#
# .. figure:: /_static/img/quickstart/comp-graph.png
#    :alt:
#
# In this network, ``w`` and ``b`` are **parameters**, which we need to
# optimize. Thus, we need to be able to compute the gradients of loss
# function with respect to those variables. In orded to do that, we set
# the ``requires_grad`` property of those tensors.
# 
#    **Note:** You can set the value of ``requires_grad`` when creating a
#    tensor, or later by using ``x.requires_grad_(True)`` method.
# 
# A function that we apply to tensors to construct computational graph is
# in fact an object of class ``Function``. This object knows how to
# compute the function in the *forward* direction, and also how to compute
# it's derivative during the *backward propagation* step. A reference to
# the backward propagation function is stored in ``grad_fn`` property of a
# tensor. You can find more information of ``Function`` `in
# documentation <https://pytorch.org/docs/stable/autograd.html#function>`__.
# 

print(z.grad_fn,loss.grad_fn,sep='\n')

######################################################################
# Computing Gradients
# -------------------
# 
# To optimize weights of parameters in the neural network, we need to
# compute the derivatives of our loss function with respect to parameters,
# namely, we need :math:`\frac{\partial loss}{\partial w}` and
# :math:`\frac{\partial loss}{\partial b}` under some fixed values of
# ``x`` and ``y``. To compute those derivatives, we call
# ``loss.backward()``, and then retrieve the values from ``w.grad`` and
# ``b.grad``:
# 

loss.backward()
print(w.grad)
print(b.grad)


######################################################################
# **Notes:** \* We can only obtain the ``grad`` properties for the leaf
# nodes of the computational graph, which have ``requires_grad`` property
# set to ``True``. For all other nodes in our graph gradients will not be
# available. \* We can only perform gradient calculations using
# ``backward`` once on a given graph, for performance reasons. If we need
# to do several ``backward`` calls on the same graph, we need to pass
# ``retain_graph=True`` to the ``backward`` call.
# 


######################################################################
# Tensor Gradients and Jacobian Products
# --------------------------------------
# 
# In many cases, we have a scalar loss function, and we need to compute
# the gradient with respect to some parameters. However, there are cases
# when the output function is an arbitrary tensor. In this case, PyTorch
# allows you to compute so-called **Jacobian product**, and not the actual
# gradient.
# 
# For a vector function :math:`\vec{y}=f(\vec{x})`, where
# :math:`\vec{x}=\langle x_1,\dots,x_n\rangle` and
# :math:`\vec{y}=\langle y_1,\dots,y_m\rangle`, a gradient of
# :math:`\vec{y}` with respect to :math:`\vec{x}` is given by **Jacobian
# matrix**:
# 
# .. math::
# 
# 
#    \begin{align}J=\left(\begin{array}{ccc}
#       \frac{\partial y_{1}}{\partial x_{1}} & \cdots & \frac{\partial y_{1}}{\partial x_{n}}\\
#       \vdots & \ddots & \vdots\\
#       \frac{\partial y_{m}}{\partial x_{1}} & \cdots & \frac{\partial y_{m}}{\partial x_{n}}
#       \end{array}\right)\end{align}
# 
# Instead of computing the Jacobian matrix itself, PyTorch allows you to
# compute **Jacobian Product** :math:`v^T\cdot J` for a given input vector
# :math:`v=(v_1 \dots v_m)`. This is achieved by calling ``backward`` with
# :math:`v` as an argument. The size of :math:`v` should be the same as
# the size of the original tensor, with respect to which we want to
# compute the product:
# 

inp = torch.eye(5,requires_grad=True)
out = (inp+1).pow(2)
out.backward(torch.ones_like(inp),retain_graph=True)
print("First call\n",inp.grad)
out.backward(torch.ones_like(inp),retain_graph=True)
print("\nSecond call\n",inp.grad)
inp.grad.zero_()
out.backward(torch.ones_like(inp),retain_graph=True)
print("\nCall after zeroing gradients\n",inp.grad)


######################################################################
# Notice that when we call ``backward`` for the second time with the same
# argument, the value of the gradient is different. This happens because
# when doing ``backward`` propagation, PyTorch **accumulates the
# gradients**, i.e. the value of computed gradients is added to the
# ``grad`` property of all leaf nodes of computational graph. If you want
# to compute the proper gradients, you need to zero out the ``grad``
# property before. In real-life training an *optimizer* helps us to do
# this.
# 
# **Note:** Previously we were calling ``backward()`` function without
# parameters. This is essentially equivalent to calling
# ``backward(torch.tensor(1.0))``, which is a useful way to compute the
# gradients in case of a scalar-valued function, such as loss during
# neural network training.
# 


######################################################################
# Disabling Gradient Tracking
# ---------------------------
# 
# By default, all tensors with ``requires_grad=True`` are tracking their
# computational history and support gradient computation. However, there
# are some cases when we do not need to do that, for example, when we have
# trained the model and just want to apply it to some input data, i.e. we
# only want to do *forward* computations through the network. We can stop
# tracking computations by surrounding our computation code with
# ``with torch.no_grad()`` block:
# 

z = torch.matmul(x,w)+b
print(z.requires_grad)

with torch.no_grad():
    z = torch.matmul(x,w)+b
print(z.requires_grad)


######################################################################
# Another way to achieve the same result is to use the ``detach()`` method
# on the tensor:
# 

z = torch.matmul(x,w)+b
z_det = z.detach()
print(z_det.requires_grad)


######################################################################
# All forward-pass computations on tensors that do not track gradients
# would be more efficient.
# 


######################################################################
# Example of Gradient Descent
# ---------------------------
# 
# Let's use the AutoGrad functionality to minimize a simple function of
# two variables :math:`f(x_1,x_2)=(x_1-3)^2+(x_2+2)^2`. We will use the
# ``x`` tensor to represent the coordinates of a point. To do the gradient
# descent, we start with some initial value :math:`x^{(0)}=(0,0)`, and
# compute each consecutive step using:
# 
# .. math::
# 
# 
#    x^{(n+1)} = x^{(n)} - \eta\nabla f
# 
# Here :math:`\eta` is so-called **learning rate** (we will call it ``lr``
# in our code), and
# :math:`\nabla f = (\frac{\partial f}{\partial x_1},\frac{\partial f}{\partial x_2})`
# is the gradient of :math:`f`.
# 
# We will start by defining the initial value of ``x`` and the function
# ``f``:
# 

x = torch.zeros(2,requires_grad=True)
f = lambda x : (x-torch.tensor([3,-2])).pow(2).sum()
lr = 0.1


######################################################################
# For the gradient descent, let's do 15 iterations. On each iteration, we
# will update the coordinate tensor ``x`` and print its coordinates to
# make sure that we are approaching the minimum:
# 

for i in range(15):
    y = f(x)
    y.backward()
    gr = x.grad
    x.data.add_(-lr*gr)
    x.grad.zero_()
    print("Step {}: x[0]={}, x[1]={}".format(i,x[0],x[1]))


######################################################################
# As you can see, we have obtained the values close to the optimal point
# :math:`(3,-2)`. Training a neural network is in fact a very similar
# process, we will need to do a number of iterations to minimize the value
# of **loss function**.
# 

##################################################################
# More help with the FashionMNIST Pytorch Blitz
# ----------------------
# `Tensors <tensor_quickstart_tutorial.html>`_
# `DataSets and DataLoaders <data_quickstart_tutorial.html>`_
# `Transformations <transforms_tutorial.html>`_
# `Build Model <build_model_tutorial.html>`_
# `Optimization Loop <optimization_tutorial.html>`_
# `AutoGrad <autograd_quickstart_tutorial.html>`_
# `Back to FashionMNIST main code base <>`_
#