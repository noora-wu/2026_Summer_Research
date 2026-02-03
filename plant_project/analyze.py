import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import csv

folder = "img"

areas = []
names = []
health_list = []
height_list = []
density_list = []

for file in sorted(os.listdir(folder)):
    if file.endswith(".jpg"):
        path = os.path.join(folder, file)
        img = cv2.imread(path)

        h, w, _ = img.shape

        crop = img[int(h*0.2):int(h*0.8),
                   int(w*0.2):int(w*0.8)]

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
