# Image Classification Web App

A simple Flask application that classifies images using PyTorch's ResNet-18 model.

## Run Locally

1. Install dependencies:
```bash
pip install flask torch torchvision pillow

2. Launch the app:
python app.py

3. Open http://localhost:5000 in your browser and upload an image.

File Structure
.
├── app.py             # Main application logic
├── model.py           # ResNet model loading
├── templates/
│   └── index.html     # Frontend interface
└── static/
    └── styles.css     # Basic CSS styling

How It Works
Uploads an image through the web interface

Resizes image to 224x224 pixels

Uses pre-trained ResNet-18 for prediction

Returns top-5 predicted classes from ImageNet

Requirements
Python 3.8+

Flask

PyTorch

Pillow