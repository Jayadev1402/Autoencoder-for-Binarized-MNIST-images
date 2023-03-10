

import torch
import torch.utils.data
from torch import nn, optim
from torch.nn import functional as F
import torchvision as thv
from torchvision import datasets
import numpy as np
import matplotlib.pyplot as plt
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') 
 
class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(196,128)
        self.fc2 = nn.Linear(128, 8 * 2)

    def forward(self, x):
        x = torch.tanh(self.fc1(x))
        x = self.fc2(x)
        mu, logvar = x[:, :8], x[:, 8:]
        return mu, logvar

#Decoder part of the Variational autoencoder, 2 layers
class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(8, 128)
        self.fc2 = nn.Linear(128, 196)

    def forward(self, z):
        z = torch.tanh(self.fc1(z))
        z = torch.sigmoid(self.fc2(z))
        return z

#Variational AutoEncoder
class VAutoencoder(nn.Module):
    def __init__(self):
        super( VAutoencoder, self).__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def forward(self, x):
        mu, logvar = self.encoder(x.contiguous().view(-1, 196))
        z = self.reparameterize(mu, logvar)
        return self.decoder(z), mu, logvar
    #Reparametrizing into mean and log variance
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

#bernouli loss as BCE loss  
def bernoulli_loss(recon_x, x):
  return F.binary_cross_entropy(recon_x, x.view(-1, 196), reduction='sum')

#KLD loss
def KLDivergence_loss(logvar,mu):
  return - torch.sum(1 + logvar - mu**2 - logvar.exp())/2

def train(num_epochs,optimizer,model,train_loader):

    model.train()
    ELBO_1=[] 
    ELBO_2= []
    #Training for 50 epochs
    for epoch in range(num_epochs):
        epoch_loss = 0

        for data, _ in train_loader:
            data = data.to(device)
            optimizer.zero_grad()

            ba, mu, logvar = model(data)
            bernoulli = bernoulli_loss(ba, data)
            KLD = KLDivergence_loss(logvar, mu)

            ELBO_1.append(bernoulli)
            ELBO_2.append(KLD)

            #Total loss
            loss = bernoulli + KLD
            loss.backward()
            epoch_loss += loss.item()
            optimizer.step()


        print('Epoch {} complete. Average loss: {:.4f}'.format(epoch + 1, epoch_loss / len(train_loader.dataset)))
    return ELBO_1, ELBO_2

def plot_loss_vs_updates(ELBO_2,ELBO_1):
    #Converting to numpy arrays
    ELBO_2= [l.detach().numpy() for l in ELBO_2]
    ELBO_1 = [l.detach().numpy() for l in ELBO_1]

    #Plotting bernoulli loss and KLD loss wrt number of weight updates
    plt.plot(ELBO_1, label='bernoulli loss')
    plt.plot(ELBO_2, label='KL Divergence loss')
    plt.xlabel('number of weight updates')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

def plot_images(x_train,model):
  f, axarr = plt.subplots(1,8,figsize=(17, 17))
  f1, axarr1 = plt.subplots(1,8,figsize=(17, 17))
  #Plot original images
  for i in range(8):
    axarr[i].imshow(x_train[i,:,:].reshape(14,14).detach().numpy())
  #Plot generated images
  for i in range(8):
    img,_,_=model(x_train[i,:,:])
    axarr1[i].imshow(img.reshape(14,14).detach().numpy())

def generate_guassian(model):
  # Sample a batch of latent variables from a Gaussian distribution
  z = torch.randn(16, 8).to(device)

  # Run the decoder network to synthesize images from the latent variables
  images = model.decoder(z)

  #Plot images
  f, axarr = plt.subplots(1,8,figsize=(17, 17))
  for i in range(8):
      axarr[i].imshow(images[i].reshape(14,14).detach().numpy() )
def main():
  train_set = thv.datasets.MNIST('./', download=True, train=True, transform=thv.transforms.ToTensor())
  val_set = thv.datasets.MNIST('./', download=True, train=False, transform=thv.transforms.ToTensor())


  index = {}
  ind=[]
  for i, catagory in enumerate(np.unique(train_set.targets)):
    
    ind = [k for k, num in enumerate(train_set.targets) if num==catagory]

    index[i] = ind


  tr_idx = []
  for catagory, idx in index.items():
    tr_idx += idx[:1000]

  np.random.shuffle(tr_idx)
  x_train = (train_set.data[tr_idx])[:,::2,::2]
  y_train = train_set.targets[tr_idx]

  #Setting values below 128 to 0 and above 128 to 1
  xx_train=x_train
  x_train[x_train<=128] = 0
  x_train[x_train>128] = 1

  #Changing the type to float
  x_train = x_train.float()

  #Train_loader
  train_loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(x_train, y_train), batch_size=100, shuffle=True)

  #Model
  model = VAutoencoder().to(device)
  optimizer = optim.Adam(model.parameters(), lr=1e-3)

  #Training
  ELBO_1, ELBO_2 = train(50,optimizer,model,train_loader)
   
  #Plots
  plot_loss_vs_updates(ELBO_2,ELBO_1)
  plot_images(x_train,model) 

  generate_guassian(model)
if __name__=="__main__":
  main()





