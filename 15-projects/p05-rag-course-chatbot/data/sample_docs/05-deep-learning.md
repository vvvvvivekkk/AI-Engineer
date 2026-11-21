# Module 05 - Deep learning

## Neurons and layers
A **neural network** is made of layers of simple units. Each unit multiplies its inputs by weights, adds them up, and passes the result through an **activation function** such as ReLU, which keeps positive numbers and turns negatives into zero.

## The training loop
Training repeats four steps for each batch: the **forward pass** makes predictions, the **loss** measures how wrong they are, **backpropagation** (`loss.backward()` in PyTorch) works out how each weight affected the loss, and the **optimiser** (for example Adam) updates the weights. One pass over the whole dataset is an **epoch**.

## CNNs
A **convolutional neural network** (CNN) slides small filters across an image. Each filter detects a pattern such as an edge or a curve, wherever it appears. **Pooling** shrinks the image and keeps the strongest signals. CNNs are the classic choice for images.

## Early stopping and dropout
**Early stopping** watches the validation loss and stops training when it stops improving, then restores the best weights. **Dropout** randomly switches off some units during training so the network cannot rely on any single one. Both fight overfitting.
