import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import csv

folder = "img"
overlay_folder = "overlay"
os.makedirs(overlay_folder, exist_ok=True)

areas = []
names = []
health_list = []
height_list = []
density_list = []

# Flag to control whether to show intermediate results
show_first_image = False  # Set to False to disable showing the first image
first_shown = False  # Control only to show the first image

from datetime import datetime

files = [f for f in os.listdir(folder) if f.endswith(".jpg")]
files_sorted = sorted(files, key=lambda x: datetime.strptime(x[:-4], "%Y-%m-%d"))

for file in files_sorted:
    if file.endswith(".jpg"):
        path = os.path.join(folder, file)
        img = cv2.imread(path)

        h, w, _ = img.shape

        # crop the image
        crop = img  # ---[int(h*0.2):int(h*0.8),int(w*0.2):int(w*0.8)]

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        # -------- Green detection --------
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # -------- Yellow detection --------
        lower_yellow = np.array([20, 40, 40])
        upper_yellow = np.array([35, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        green_pixels = np.sum(green_mask > 0)
        yellow_pixels = np.sum(yellow_mask > 0)

        # -------- Area --------
        area = green_pixels

        # -------- Health index --------
        health = green_pixels / (green_pixels + yellow_pixels + 1)

        # -------- Height --------
        rows = np.where(green_mask > 0)[0]
        if len(rows) > 0:
            height = green_mask.shape[0] - rows.min()
        else:
            height = 0

        # -------- Density --------
        density = green_pixels / green_mask.size

        areas.append(area)
        health_list.append(health)
        height_list.append(height)
        density_list.append(density)
        names.append(file)

        print(file,
              "Area:", area,
              "Health:", round(health, 3),
              "Height:", height)

        # -------- Create overlay for all images --------
        # Convert mask to color
        green_rgb = cv2.cvtColor(green_mask, cv2.COLOR_GRAY2BGR)
        green_rgb[:, :, 0] = 0  # Blue channel
        green_rgb[:, :, 1] = 255  # Green channel
        green_rgb[:, :, 2] = 0  # Red channel

        yellow_rgb = cv2.cvtColor(yellow_mask, cv2.COLOR_GRAY2BGR)
        yellow_rgb[:, :, 0] = 0  # Blue channel
        yellow_rgb[:, :, 1] = 255  # Green channel
        yellow_rgb[:, :, 2] = 255  # Red channel (黄色 = 红+绿)

        # Create overlay by combining original image with colored masks
        overlay = crop.copy()
        overlay[green_mask > 0] = green_rgb[green_mask > 0]
        overlay[yellow_mask > 0] = yellow_rgb[yellow_mask > 0]

        # Save overlay to overlay folder
        overlay_path = os.path.join(overlay_folder, file)
        cv2.imwrite(overlay_path, overlay)

        # -------- Visualization (only show the first image) --------
        if show_first_image and not first_shown:
            plt.figure(figsize=(6,6))
            plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
            plt.title(f"Overlay Green + Yellow: {file}")
            plt.axis("off")
            plt.show()
            first_shown = True  # 标记已经显示过第一张


# -------- Growth speed --------
growth_rate = np.diff(areas)
growth_rate = np.insert(growth_rate, 0, 0)

# -------- Anomaly detection --------
threshold = np.std(growth_rate) * 2
anomalies = np.where(abs(growth_rate) > threshold)[0]

print("\nDetected anomalies:")
for idx in anomalies:
    print("Index:", idx, "Image:", names[idx])

# -------- Save CSV --------
with open("plant_analysis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Image", "Area", "Health",
        "Height", "Density",
        "GrowthRate", "Anomaly"
    ])

    for i in range(len(names)):
        writer.writerow([
            names[i],
            areas[i],
            health_list[i],
            height_list[i],
            density_list[i],
            growth_rate[i],
            1 if i in anomalies else 0
        ])

print("CSV saved")

# -------- Plot growth --------
plt.plot(areas, label="Area")
if len(anomalies) > 0:
    plt.scatter(anomalies,
                np.array(areas)[anomalies],
                label="Anomaly")
plt.legend()
plt.title("Plant Area Growth")
plt.show()

# -------- Plot health --------
plt.plot(health_list)
plt.title("Health Index")
plt.show()

# -------- Plot height --------
plt.plot(height_list)
plt.title("Plant Height")
plt.show()

# -------- Prediction --------
x = np.arange(len(areas))
coef = np.polyfit(x, areas, 1)
trend = np.poly1d(coef)

future_x = np.arange(len(areas) + 30)
future_y = trend(future_x)

plt.plot(areas, label="Observed")
plt.plot(future_y, label="Predicted")
plt.legend()
plt.title("Growth Prediction")
plt.show()
