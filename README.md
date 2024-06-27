# Still-SR-GUI

Still-SR-GUI is a graphical user interface application built with PySide6 for performing 4x and 2x Super-Resolution on still images using the DiffIR model in the ONNX format. The application allows the user to study the quality enhancements by the DiffIR model to their input image.

## Features

- **Super Resolution Options:**
  - Perform 4x and 2x Super-Resolution on a 100x100 crop of still images.
  - Toggle between viewing the entire input image and the cropped region sent as input to the model.
  - Adjust the center of the crop interactively on the whole input image.
  - Select the image file using drag and drop functionality.

- **Views:**
  - **Input View:** Display the input image. Toggle between whole image and crop view. Adjust crop center interactively.
  - **Duplicate View:** Display the Super-Resolved input crop using duplication method.
  - **Output View:** Display the output of the Super-Resolution model.

- **Model Selection:**
  - Switch between 4x and 2x Super-Resolution models.

- **Multithreading:**
  - Model execution runs on a separate thread to prevent GUI freezing during processing.

## Future Development

- **Optimized ONNX Session Handling:**
  - Implement creation and execution of the ONNX session on a separate thread to avoid GUI freeze when switching between 4x and 2x models.
  
- **GPU Optimization:**
  - Currently optimized for CPU execution. Future work includes creating a data pipeline and optimizing ONNX model execution on GPUs for improved performance.

## Installation

To run the Still-SR-GUI locally, follow these steps:

1. Clone the repository:
```
git clone https://github.com/VinatG/Still-SR-GUI.git
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python main.py
```

## Usage

- Open the application and load an image using drag and drop or file menu.
- Use the toggle button in the Input view to switch between whole image and crop view.
- Adjust the crop center on the whole image view.
- Select 4x or 2x model in the GUI.
- View the duplicated Super-Resolved crop in the Duplicate view and output in the Output view.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your improvements.

## References

- **DiffIR Paper:** [Link to DiffIR Paper](https://arxiv.org/pdf/2303.09472)
- **DiffIR GitHub Repository:** [Link to DiffIR GitHub Repository](https://github.com/Zj-BinXia/DiffIR/tree/master)




