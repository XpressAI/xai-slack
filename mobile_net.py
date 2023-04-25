from xai_components.base import InArg, OutArg, InCompArg, BaseComponent, Component, xai_component

import io
import os
import torch
import urllib.request
import torchvision.transforms as T
from PIL import Image
from torchvision.models import mobilenet_v2

@xai_component
class MobileNetV2ProcessImageData(Component):
    """Processes image data using the MobileNetV2 model and returns the predicted class label.
    ##### inPorts:
    - image_data: Input image data in bytes.
    ##### outPorts:
    - prediction: Predicted class label for the input image.
    """

    image_data: InArg[bytes]
    prediction: OutArg[str]

    def execute(self, ctx) -> None:
        # Load the image from the image_data bytes
        image = Image.open(io.BytesIO(self.image_data.value))

        # Load the MobileNetV2 model
        model = mobilenet_v2(pretrained=True)
        model.eval()

        # Preprocess the image and prepare it for the MobileNetV2 model
        preprocess = T.Compose([
            T.Resize(256),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        input_image = preprocess(image).unsqueeze(0)

        # Get the prediction using the MobileNetV2 model
        with torch.no_grad():
            output = model(input_image)
            _, prediction_idx = torch.max(output, 1)
            prediction_idx = prediction_idx.item()

        # Download the imagenet_classes.txt file if it doesn't exist
        file_path = "imagenet_classes.txt"
        if not os.path.exists(file_path):
            url = "https://gist.githubusercontent.com/yrevar/942d3a0ac09ec9e5eb3a/raw/238f720ff059c1f82f368259d1ca4ffa5dd8f9f5/imagenet1000_clsidx_to_labels.txt"
            urllib.request.urlretrieve(url, file_path)

        # Convert the prediction index to a human-readable class label
        with open(file_path, "r") as f:
            labels = [line.strip() for line in f.readlines()]

        self.prediction.value = labels[prediction_idx]