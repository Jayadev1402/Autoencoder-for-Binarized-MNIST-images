# Autoencoder-for-Binarized-MNIST-images
In this project, we propose an autoencoder architecture for binarized MNIST images. The autoencoder consists of an encoder and a decoder. The encoder maps an input image to a latent factor, and the decoder maps the latent factor back to the input image.

Encoder
The encoder consists of two fully-connected layers. The first layer has 14x14 = 19642 inputs and 128 outputs. The activation function used in this layer is tanh. The second layer has 128 inputs and 1643 outputs. This layer does not have an activation function. The output of this layer is the latent factor, which has 8 output neurons for the mean and 8 more for the standard deviation.

Decoder
The decoder takes the latent factor as input, which has 8 inputs. The decoder pushes the input through one layer with 128 outputs and tanh activation function. The second layer has 19642 output neurons and sigmoid activation function. The final output of the decoder is the reconstructed image.

Note that the final nonlinearity of the decoder should be sigmoid because we want to reconstruct binarized MNIST images.

Results
The results of the model will be presented here.

Conclusion
In this project, we proposed an autoencoder architecture for binarized MNIST images. The encoder maps an input image to a latent factor, and the decoder maps the latent factor back to the input image. The results show that the proposed architecture is effective in reconstructing binarized MNIST images.
