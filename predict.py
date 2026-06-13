"""
predict.py — Cataract Detection Model Inference
Loads best_cataract_model.pth and runs prediction on a single image.
"""

import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
from PIL import Image


# ── Model Architecture ──────────────────────────────────────────────────────
class CataractDetectorMobileNet(nn.Module):
    """
    MobileNetV2 backbone with a custom classifier head.
    Matches the architecture used during training:
      - Frozen MobileNetV2 feature extractor
      - AdaptiveAvgPool2d → Flatten
      - Linear(1280, 500) → ReLU → Dropout(0.2) → Linear(500, 2)
    """

    def __init__(self, size_inner: int = 500, droprate: float = 0.2, num_classes: int = 2):
        super(CataractDetectorMobileNet, self).__init__()

        # Pre-trained MobileNetV2 backbone
        self.base_model = models.mobilenet_v2(weights="IMAGENET1K_V1")

        # Freeze backbone parameters
        for param in self.base_model.parameters():
            param.requires_grad = False

        # Remove original classifier head
        self.base_model.classifier = nn.Identity()

        # Custom classifier head
        self.global_avg_pooling = nn.AdaptiveAvgPool2d((1, 1))
        self.inner = nn.Linear(1280, size_inner)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(droprate)
        self.output_layer = nn.Linear(size_inner, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.base_model.features(x)
        x = self.global_avg_pooling(x)
        x = torch.flatten(x, 1)
        x = self.inner(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.output_layer(x)
        return x


# ── Constants ────────────────────────────────────────────────────────────────
CLASS_NAMES = ["cataract", "normal"]  # sorted, matches training directory order

INPUT_SIZE = 224

# ImageNet normalization — same values used during training
MEAN = [0.485, 0.456, 0.406]
STD  = [0.229, 0.224, 0.225]

# Inference transform (no augmentation)
INFERENCE_TRANSFORM = transforms.Compose([
    transforms.Resize((INPUT_SIZE, INPUT_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=MEAN, std=STD),
])


# ── Model Loader ─────────────────────────────────────────────────────────────
def load_model(model_path: str = "best_cataract_model.pth") -> torch.nn.Module:
    """
    Instantiate the model and load the saved weights.

    Args:
        model_path: Path to the .pth state-dict file.

    Returns:
        model in eval mode on the correct device.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CataractDetectorMobileNet(size_inner=500, droprate=0.2, num_classes=2)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model


# ── Prediction ───────────────────────────────────────────────────────────────
def predict(image: Image.Image, model: torch.nn.Module) -> dict:
    """
    Run inference on a single PIL image.

    Args:
        image:  PIL Image (RGB).
        model:  Loaded model in eval mode.

    Returns:
        dict with keys:
            - label       (str)  : predicted class name
            - confidence  (float): probability of predicted class (0–1)
            - probabilities (dict): {class_name: probability} for all classes
    """
    device = next(model.parameters()).device

    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    tensor = INFERENCE_TRANSFORM(image).unsqueeze(0).to(device)  # [1, 3, 224, 224]

    with torch.no_grad():
        logits = model(tensor)                          # [1, 2]
        probs  = torch.softmax(logits, dim=1).squeeze() # [2]

    probs_list = probs.cpu().tolist()
    predicted_idx = int(torch.argmax(probs).item())

    return {
        "label":         CLASS_NAMES[predicted_idx],
        "confidence":    round(probs_list[predicted_idx], 4),
        "probabilities": {
            name: round(prob, 4)
            for name, prob in zip(CLASS_NAMES, probs_list)
        },
    }


# ── CLI usage ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)

    img_path = sys.argv[1]
    img = Image.open(img_path)
    mdl = load_model("best_cataract_model.pth")
    result = predict(img, mdl)

    print(f"\nPrediction : {result['label'].upper()}")
    print(f"Confidence : {result['confidence'] * 100:.2f}%")
    print("Class probabilities:")
    for cls, prob in result["probabilities"].items():
        print(f"  {cls:>10}: {prob * 100:.2f}%")
