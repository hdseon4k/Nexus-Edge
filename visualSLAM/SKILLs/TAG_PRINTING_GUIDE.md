# Skill: AprilTag Printing & Scaling for SLAM

## 1. Why Physical Size Matters
SLAM calculates distance based on the ratio of the **known physical size** of the tag to its **pixel size** in the image. If your map says the tag is 0.1m but it's printed at 0.15m, all your distance estimates will be off by 50%.

## 2. A4 Printing Tips
- **No Scaling:** When printing from a PDF or Image viewer, select **"Actual Size"** or **"100% Scale"**. Do NOT use "Fit to Page".
- **High Contrast:** Ensure the black is deep black and the white border (quiet zone) is clean.
- **Flatness:** Glue the paper to a rigid board (foam board, acrylic) to prevent warping.

## 3. Measuring
Use a digital caliper or a precise ruler to measure the **side length of the black square** (excluding the white border).

Example:
- Printed size: 16.5 cm
- Value for code: `tag_size = 0.165` (meters)
