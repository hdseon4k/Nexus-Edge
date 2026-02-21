import os
from ultralytics import YOLO

def train_barcode_model():
    """
    Fine-tune YOLOv11n on the custom barcode dataset.
    """
    # 1. Load the base YOLO11n model (Pre-trained on COCO)
    model = YOLO("yolo11n.pt")

    # 2. Set the path to the data configuration file
    # This path is relative to the current working directory or absolute
    data_yaml_path = os.path.abspath("datasets/barcode/data.yaml")

    print(f"Starting training with data config: {data_yaml_path}")

    # 3. Start Fine-tuning (Transfer Learning)
    # Parameters can be tuned based on your GPU capability
    results = model.train(
        data=data_yaml_path,
        epochs=100,          # Adjust based on convergence
        imgsz=640,           # Standard resolution
        batch=16,            # Adjust based on VRAM
        device="0",          # Use "0" for NVIDIA GPU, "cpu" for CPU
        project="models",    # Save results to 'models' folder
        name="barcode_yolo11n",
        exist_ok=True,       # Overwrite if exists
        pretrained=True,     # Use pre-trained weights
        optimizer="auto",    # SGD, Adam, AdamW, etc.
        verbose=True
    )

    print("Training Complete!")
    print(f"Best model saved at: {results.save_dir}/weights/best.pt")

if __name__ == "__main__":
    # Create source directory if it doesn't exist (though it should already)
    os.makedirs("src", exist_ok=True)
    
    # Check if data.yaml exists before starting
    if not os.path.exists("datasets/barcode/data.yaml"):
        print("Error: datasets/barcode/data.yaml not found. Please ensure the folder structure is correct.")
    else:
        train_barcode_model()
