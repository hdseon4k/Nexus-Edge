# CVAT Labeling Guide for Barcode Detection

This guide explains how to use CVAT (Computer Vision Annotation Tool) to create a custom dataset for YOLOv11n barcode detection.

## 1. Preparation
1. Access [CVAT.ai](https://app.cvat.ai/) or your self-hosted instance.
2. Create a free account if using the cloud version.

## 2. Setting Up Project & Task
1. **Create Project**: 
   - Name: `Barcode Detection`
   - Labels: Add a label named `barcode` (Color: any).
2. **Create Task**:
   - Give it a name (e.g., `Set 01 - PC Capture`).
   - Project: Select the `Barcode Detection` project.
   - **Upload Data**: Drag and drop your images from PC into the upload area.
   - Click **Submit & Open**.

## 3. Labeling Process
1. Open the task and click on a job.
2. Use the **Draw new rectangle** tool (`Shift + N`).
3. Draw a box around each barcode in the image.
4. Ensure the label is set to `barcode`.
5. Press `Ctrl + S` frequently to save your progress.

## 4. Exporting to YOLO Format
1. Once labeling is complete, go back to the **Tasks** list.
2. Click the three dots (...) next to your task and select **Export job dataset**.
3. **Export Format**: Select **YOLO 1.1**.
4. Enable **Save images** if you want them zipped together.
5. Click **OK** to download the `.zip` file.

## 5. Integrating with Nexus-Edge
1. Unzip the downloaded file.
2. Move the images and labels to the following project structure:
   - Images to: `datasets/barcode/images/train` (or `/val`)
   - Labels to: `datasets/barcode/labels/train` (or `/val`)
3. Ensure the `.txt` label files have the same base name as their corresponding image files.

> [!TIP]
> Use a 80-20 split for training and validation sets for better model evaluation.
