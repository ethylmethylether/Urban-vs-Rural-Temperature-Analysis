# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 17:07:25 2025

@author: Uzair
"""

import rasterio
from rasterio.mask import mask
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


# Loading files

urban = gpd.read_file("data/local-area-boundary.geojson")  # Vancouver Polygon
rural = gpd.read_file("data/rural-area-boundary.geojson")  # Surrounding Polygon

# Loading Landsat LST TIFF
lst_path = "tiff/LST_ST_B10.tif"
lst_raster = rasterio.open(lst_path)

# Reprojecting to same crs
urban_proj = urban.to_crs(lst_raster.crs)
rural_proj = rural.to_crs(lst_raster.crs)


# Clipping the tif file to our desired polygons
def clip_raster_by_shape(raster, shapes):
    out_image, out_transform = mask(raster, shapes, crop=True)
    out_meta = raster.meta.copy()
    out_meta.update({
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })
    return out_image[0], out_meta


# Extracting geometries
urban_shapes = [feature["geometry"] for feature in urban_proj.__geo_interface__["features"]]
rural_shapes = [feature["geometry"] for feature in rural_proj.__geo_interface__["features"]]

# Filtering rural data because its big
urban_buffer = urban_proj.geometry.buffer(20000)
rural_filtered = rural_proj[rural_proj.geometry.intersects(urban_buffer.geometry.union_all())]
rural_filtered_shapes = [feature["geometry"] for feature in rural_filtered.__geo_interface__["features"]]

# Clipping using the function
urban_clip, urban_meta = clip_raster_by_shape(lst_raster, urban_shapes)
rural_clip, rural_meta = clip_raster_by_shape(lst_raster, rural_filtered_shapes)

# Apply scale factor (try 0.1 first)
urban_scaled = urban_clip * 0.1
rural_scaled = rural_clip * 0.1

# Convert Kelvin to Celsius
urban_celsius = urban_scaled - 273.15
rural_celsius = rural_scaled - 273.15


def calculate_stats(arr):
    arr = arr[arr > 0]  # only valid pixels
    mean = np.mean(arr)
    median = np.median(arr)
    perc95 = np.percentile(arr, 95)
    return mean, median, perc95


urban_stats = calculate_stats(urban_celsius)
rural_stats = calculate_stats(rural_celsius)

# metadata
scene_metadata = {
    "Scene Date": "2024-08-09",
    "Product Generated Date": "2024-08-15",
    "Day/Night": "DAY",
    "Land Cloud Cover (%)": 18.28,
    "Scene Cloud Cover (%)": 15.57,
    "Satellite Station": "LGN"
}

print("\n--- Landsat Scene Metadata ---")
for key, value in scene_metadata.items():
    print(f"{key}: {value}")


print("Urban LST (°C): Mean = {:.2f}, Median = {:.2f}, Max = {:.2f}".format(*urban_stats))
print("Rural LST (°C): Mean = {:.2f}, Median = {:.2f}, Max = {:.2f}".format(*rural_stats))


def mask_invalid(arr):
    masked = np.ma.masked_where((arr <= 0) | (arr > 45), arr)
    return masked


urban_masked = mask_invalid(urban_celsius)
rural_masked = mask_invalid(rural_celsius)



#----------------Plotting------------------#

fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# ---------------- Urban Map ---------------- #
urban_bounds = urban_proj.total_bounds
urban_proj.plot(ax=axs[0], color='blue', edgecolor='green', alpha=0.5, label='Urban')
axs[0].set_xlim(urban_bounds[0], urban_bounds[2])
axs[0].set_ylim(urban_bounds[1], urban_bounds[3])
axs[0].axis('off')
axs[0].set_title("Urban Area (Vancouver)")

# ---------------- Rural Map ---------------- #
urban_buffer = urban_proj.geometry.buffer(20000)
rural_zoomed = rural_proj[rural_proj.geometry.intersects(urban_buffer.geometry.union_all())]
rural_bounds = rural_zoomed.total_bounds

# Plot rural polygons
rural_zoomed.plot(ax=axs[1], color='lightgreen', edgecolor='darkgreen', alpha=0.5, label='Rural')

# Add pointer
pointer = rural_zoomed.geometry.centroid.iloc[0]
pointer_x, pointer_y = pointer.x, pointer.y
axs[1].plot(pointer_x, pointer_y, marker='o', color='red', markersize=5)
axs[1].text(pointer_x + 600, pointer_y + 2000, 'Rural Area', color='red')

# Zoom to rural bounds
axs[1].set_xlim(rural_bounds[0], rural_bounds[2])
axs[1].set_ylim(rural_bounds[1], rural_bounds[3])
axs[1].axis('off')
axs[1].set_title("Zoomed Rural Area Around Vancouver")
plt.tight_layout()
fig.savefig("output/urban_rural_maps.png", dpi=300)
plt.show()


# ---------------- Temperature Maping ---------------- #
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Plot Urban Temperature
urban_img = axs[0].imshow(urban_masked, cmap='plasma', vmin=15, vmax=25)
axs[0].set_title("Urban Surface Temperature (°C)")
axs[0].axis('off')
fig.colorbar(urban_img, ax=axs[0], fraction=0.046, pad=0.04)

# Plot Rural Temperature
rural_img = axs[1].imshow(rural_masked, cmap='plasma', vmin=15, vmax=25)
axs[1].set_title("Rural Surface Temperature (°C)")
axs[1].axis('off')
fig.colorbar(rural_img, ax=axs[1], fraction=0.046, pad=0.04)
fig.suptitle("Urban vs Rural Surface Temperature\nLandsat Scene Date: 2024-08-09, Cloud Cover: 18.28%", fontsize=14)
plt.tight_layout()
fig.savefig("output/temperature_maps.png", dpi=300)
plt.show()

# ---------------- Bar Plot ---------------- #
# Data for plotting
labels = ['Mean', 'Median', 'Max']
urban_vals = list(urban_stats)
rural_vals = list(rural_stats)

x = np.arange(len(labels))  # label locations
width = 0.35  # bar width

fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar(x - width/2, urban_vals, width, label='Urban', color='tab:blue')
bars2 = ax.bar(x + width/2, rural_vals, width, label='Rural', color='tab:green')

# Labels and titles
ax.set_ylabel('T emperature (°C)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(loc='center right', bbox_to_anchor=(-0.15, 0.5))

# Add data labels on top of bars
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

add_labels(bars1)
add_labels(bars2)
fig.suptitle("Urban vs Rural Surface Temperature Statistics\nLandsat Scene Date: 2024-08-09, Product Generated: 2024-08-15", fontsize=14)
plt.tight_layout()
fig.savefig("output/temperature_stats_barplot.png", dpi=300)
plt.show()

import pandas as pd

data = {
    "Statistic": ['Mean', 'Median', 'Max'],
    "Urban_LST_C": urban_stats,
    "Rural_LST_C": rural_stats
}

df = pd.DataFrame(data)
df.to_csv("output/urban_rural_LST_stats.csv", index=False)






















