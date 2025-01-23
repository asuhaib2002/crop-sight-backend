import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt

# Define the CNN model
class CNNModel(nn.Module):
    def __init__(self, n_classes):
        super(CNNModel, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2, padding=0),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2, padding=0),

            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2, padding=0),

            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2, padding=0),
            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 1 * 1, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(64, n_classes)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

class PredictionService:
    def __init__(self, model_path, class_names, device=None):
        """Initialize the PredictionService with the model and configurations."""
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = class_names
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

    def _load_model(self, model_path):
        """Load the trained model from the specified path."""
        model = CNNModel(n_classes=len(self.class_names))
        # model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))

        model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        model.to(self.device)
        model.eval()
        return model

    def _preprocess_image(self, image_file):
        """Preprocess the input image for model inference."""
        image = Image.open(image_file)
        image_for_plotting = image.copy()
        image = self.transform(image).unsqueeze(0)  # Add batch dimension
        return image, image_for_plotting

    def predict(self, image_file):
        """Run prediction on the given image file and return results."""
        image, image_for_plotting = self._preprocess_image(image_file)
        image = image.to(self.device)

        with torch.no_grad():
            output = self.model(image)
            probs = F.softmax(output, dim=1)
            confidences, predicted = probs.max(1)

        predicted_class = self.class_names[predicted.item()]
        confidence = confidences.item() * 100

        return {
            "predicted_class": predicted_class,
            "confidence": confidence
        }
