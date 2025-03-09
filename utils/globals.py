from PySide6.QtCore import QUrl
from utils.utils import resource_path

# Name of DiffIR model for the respective scale
model_scale_map = {'2x' : 'realworldsr-diffirs2-ganx2-v2', '4x' : 'realworldsr-diffirs2-ganx4-v2'}

# Default media paths
default_image_path = QUrl.fromLocalFile(resource_path('default/GRID.jpg'))
default_video_path = QUrl.fromLocalFile(resource_path('default/TestVideo0640x0480.mp4'))

# Onnx session paths
ocr_det_model_path = './ONNX_models/paddle_det_model.onnx'
ocr_rec_model_path = './ONNX_models/paddle_rec_model.onnx'
sr_model_paths = {2 : './ONNX_models/RealworldSR-DiffIRS2-GANx2-V2.onnx', 4 : './ONNX_models/RealworldSR-DiffIRS2-GANx4-V2.onnx'}

providers = [ ('CUDAExecutionProvider', {"cudnn_conv_algo_search" : "DEFAULT"}), 'CPUExecutionProvider']

# Links to the Diffir paper an github repository
diffir_github_link = '<a href="https://github.com/Zj-BinXia/DiffIR">GitHub Repository</a>'
diffir_paper_link = '<a href="https://arxiv.org/pdf/2303.09472.pdf">Research Paper</a>'

# Execution provider in order of preference
providers = [ ('CUDAExecutionProvider', {"cudnn_conv_algo_search" : "DEFAULT"}), 'CPUExecutionProvider']

# Drop-down for post-processing
POST_PROCESSING_OPTIONS = {
    "No Post-Processing": "no_processing",
    "Histogram Equalization": "histogram_equalization",
    "Identity": "identity"
}

app_style = """
QPushButton {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #cccccc;
    padding: 5px;
}
QPushButton::hover {
    background-color: #e0e0e0;
}
QPushButton::pressed {
    background-color: #d0d0d0;
}

QComboBox {
    min-height: 20px;
    min-width: 150px; /* Adjust width as needed */
}

/* Hover effect */
QComboBox:hover {
    background-color: #e0e0e0;
}

/* Pressed effect */
QComboBox:pressed {
    background-color: #d0d0d0;
}
"""