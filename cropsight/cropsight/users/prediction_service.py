# import torch
# from torchvision import datasets, transforms
# from torch.utils.data import DataLoader, random_split
# import torch.nn as nn
# import torch.optim as optim
# import matplotlib.pyplot as plt
# import numpy as np
# from torch.optim import lr_scheduler
# from torchvision import datasets, models, transforms
# from torch.utils.data import ConcatDataset
# from sklearn.metrics import precision_score, recall_score, confusion_matrix
# import seaborn as sns
# from PIL import Image
# from torchvision.models import vgg16, VGG16_Weights
# from torchvision.models import ResNet50_Weights, resnet50
# import copy
# import os
# import time

# class PredictionService:

#     def __init__(self, model_path: str):
#         self.model = load_model(model_path)
#         self.model_path = model_path
#         self.image_size = 224
#         self.channels = 3
#         self.n_classes = 3
#         self.batch_size = 32
#         self.epochs = 30
        
   