import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from .exceptions import UndefinedDiseaseError
from .dtos.response.response_dataclass import PredictionResponseData
from .models import Products

class CNNModel(nn.Module):
    def __init__(self, n_classes):
        super(CNNModel, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Dropout2d(0.3),
            nn.MaxPool2d(2)
        )

        self.fc_layers = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, n_classes)
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
        if confidence < 75:
            raise UndefinedDiseaseError("Cannot classify, please upload a clear image")

        products = Products.objects.filter(category__name=predicted_class).order_by('?')[:10]
        additional_info_message = ''
        # 'Late_Blight'['Brown_Rust', 'Healthy', 'Yellow_Rust']bacterial_blight', 'curl_virus', 'fussarium_wilt', 'healthy'
        if predicted_class == "healthy" or predicted_class == "Healthy":
            additional_info_message = (
        "No disease detected. Your plant appears to be in good health! "
        "To maintain plant health, ensure proper watering, fertilization, and pest control. "
        "Regular monitoring will help catch any early signs of disease."
        )

        elif predicted_class == "bacterial_blight":
            additional_info_message = (
                "Bacterial blight is a serious disease caused by Xanthomonas bacteria. It leads to yellowing, wilting, and dark spots on leaves, eventually causing defoliation. "
                "To manage this disease: \n"
                "- Remove and destroy infected plant parts. \n"
                "- Avoid overhead watering, as moisture spreads bacteria. \n"
                "- Use copper-based fungicides to control its spread. \n"
                "- Ensure good air circulation around plants to reduce humidity."
            )

        elif predicted_class == "curl_virus":
            additional_info_message = (
                "Curl virus, commonly known as Leaf Curl Virus, is a viral disease that causes leaves to curl, twist, and develop a leathery texture. It spreads through whiteflies. "
                "To manage this disease: \n"
                "- Remove and destroy infected plants to prevent further spread. \n"
                "- Use insecticidal soaps or neem oil to control whiteflies. \n"
                "- Maintain proper plant spacing for good airflow. \n"
                "- Grow virus-resistant plant varieties if available."
            )

        elif predicted_class == "fussarium_wilt":
            additional_info_message = (
                "Fusarium wilt is a fungal disease that infects the plant's vascular system, causing wilting, yellowing, and eventual plant death. It thrives in warm, moist soil. "
                "To manage this disease: \n"
                "- Remove and dispose of infected plants immediately. \n"
                "- Rotate crops to prevent fungal buildup in the soil. \n"
                "- Improve soil drainage and avoid overwatering. \n"
                "- Use resistant plant varieties when possible. \n"
                "- Sterilize gardening tools to avoid spreading the fungus."
            )

        elif predicted_class == "Early_Blight":
            additional_info_message = (
                "Early blight, caused by Alternaria solani, affects tomato and potato plants, creating brown spots with concentric rings on leaves. It weakens plants and reduces yield. "
                "To manage this disease: \n"
                "- Remove affected leaves and avoid overhead watering. \n"
                "- Use fungicides containing chlorothalonil or copper. \n"
                "- Rotate crops and avoid planting tomatoes or potatoes in the same soil each year. \n"
                "- Ensure good spacing between plants for airflow."
            )

        elif predicted_class == "Late_Blight":
            additional_info_message = (
                "Late blight, caused by Phytophthora infestans, is a devastating fungal-like disease that spreads rapidly in cool, humid conditions, causing dark lesions on leaves and fruit. "
                "To manage this disease: \n"
                "- Remove infected plants immediately and destroy them. \n"
                "- Apply fungicides with mancozeb or copper sulfate as a preventive measure. \n"
                "- Avoid overhead watering and keep leaves dry. \n"
                "- Choose disease-resistant plant varieties."
            )

        elif predicted_class == "Brown_Rust":
            additional_info_message = (
                "Brown rust (or Leaf Rust) is a fungal disease affecting cereal crops like wheat and barley. It forms small brown pustules on leaves, reducing photosynthesis and yield. "
                "To manage this disease: \n"
                "- Use fungicides containing triazoles or strobilurins. \n"
                "- Remove infected leaves to slow the spread. \n"
                "- Plant rust-resistant crop varieties. \n"
                "- Avoid excessive nitrogen fertilization, which makes plants more susceptible."
            )

        elif predicted_class == "Yellow_Rust":
            additional_info_message = (
                "Yellow rust (or Stripe Rust) is a fungal disease that affects wheat and other cereals. It creates yellow streaks along the leaves and reduces grain production. "
                "To manage this disease: \n"
                "- Apply fungicides early, especially those with triazole or QoI (strobilurin) ingredients. \n"
                "- Grow resistant crop varieties when available. \n"
                "- Practice crop rotation to reduce fungal spores in the soil. \n"
                "- Ensure good plant nutrition to improve resistance."
            )

        return PredictionResponseData.generate_response(predicted_class, confidence, additional_info_message, products)
