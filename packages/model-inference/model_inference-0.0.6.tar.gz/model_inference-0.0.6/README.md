# Torch CUDA install

If the identity_clustering package is installing the CPU version, you can install the right CUDA versions by manually installing it or running the following command:

``` bash
python -m model_inference.torch_install
```

# *Sphinx Documentation*

To view Sphinx documentation, clone this repository and run the following commands

``` bash
cd pkg-faceswap-inference

#install sphinx and a theme.
pip install sphinx
pip install sphinx-rtd-theme

# generate docs
sphinx-build -b html docs/ build/
```
open the build folder there you will  find `index.html` , open it with a browser

---


# Inference Class Documentation

The `Inference` class provides functionalities for inferencing video files with models. It includes utilities for timing and tracking nested function calls to aid in performance analysis.

## Table of Contents
- [Class Attributes](#class-attributes)
- [Methods](#methods)
- [Usage](#usage)
- [License](#license)

---

## Class Attributes
- `device (str)`: Specifies the device (`cpu` or `cuda`) used for computation.
- `shape (tuple)`: Dimensions for resizing clustered faces, default is `(224, 224)`.
- `classes (list)`: The categories the model can predict, such as `["Real", "Fake"]`.
- `timings (dict)`: Stores timing data for functions with nested call relationships.
- `_clusters (None or dict)`: Stores clusters of faces post-clustering.

---

## Methods

### `__init__(self, device: str, shape=(224, 224))`
- Initializes the `Inference` class with specified device and shape attributes.

### `generate_video_data(self, video_path: str, print_timings=True)`
- Processes a video to detect, crop, and cluster faces, and converts them to RGB format.

### `get_data(self, video_path: str, print_timings=True)`
- Retrieves essential data for frames, bounding boxes, images, FPS, and clustered identities from a video.

### `get_predictions(self, model, images: torch.Tensor, device='cuda')`
- Runs predictions on clustered face images using a model and returns logits and labels.

### `__cvt_to_rgb(self, faces: tuple) -> torch.Tensor`
- Converts images from BGR to RGB format.

### `__plot_images_grid(self, tensor: torch.Tensor, images_per_row=4)`
- Plots a grid of images from a 4D tensor.

### `__print_result(self, result: dict, image_data: List[torch.Tensor])`
- Displays results, including images, based on the model’s predictions.

### `__print_timings(self, timings: dict)`
- Outputs timing information for functions with nested call relationships.

### `__create_sequence_dict(self, identity_data)`
- Organizes identity information into a sequence dictionary.

### `__draw_bounding_boxes(self, video_path: str, sequence_dict, result_video_path: str)`
- Draws bounding boxes on faces in the video and saves the processed output.

### Decorator `timeit(func)`
- Times functions and records their nested relationships in the `timings` attribute.

---

## Usage

Here's a simple example of using the `Inference` class:

```python
from inference import Inference
import torch
from models.models_list import ModelList

# Initialize Inference class
device = "cuda" if torch.cuda.is_available() else "cpu"
inference = Inference(device=device)

# Load your model from ModelList
model = ModelList().load_model("face_detection_model", device)

# Process video
video_path = "/path/to/video.mp4"
output_data, num_clusters = inference.generate_video_data(video_path)

# Get predictions for each cluster
for cluster_images in output_data:
    predictions = inference.get_predictions(model, cluster_images, device)
    inference.__print_result(predictions, cluster_images)
```

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---
