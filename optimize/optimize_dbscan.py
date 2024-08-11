import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from utils import *

# Read the Data and Convert to Rectangular Coordinates
file_path = "C:/lidar_data/data_20s.csv"
lidar_data = read_lidar_data(file_path)
rectangular_coords = convert_lidar_data_to_rectangular(lidar_data)

# Flatten the list of frames into a single DataFrame for NearestNeighbors calculation
all_points = np.vstack(rectangular_coords)

# Standardizing the data might not be necessary for LiDAR coordinates, but it depends on the specific distribution

# Finding optimal eps using NearestNeighbors


# You can visually identify the elbow point in this plot to choose the eps
# Then set up a range around this eps value and different min_samples values to tune

# Example to iterate over a range of eps and min_samples values to find the best configuration based on silhouette score

best_score = -1
best_params = (None, None)

eps = 0.14
min_samples_range = range(5, 21)  # From 5 to 20

for min_samples in min_samples_range:
    print(f"Testing min_samples={min_samples}")  # To track progress
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(all_points)
    labels = db.labels_
    print(f"Number of clusters: {len(set(labels)) - (1 if -1 in labels else 0)}, Noise points: {np.sum(labels == -1)}")

    # Ensure we have more than one cluster and less noise
    if len(set(labels)) > 1 and np.sum(labels != -1) > 0:
        score = silhouette_score(all_points, labels)
        if score > best_score:
            best_score = score
            best_params = (eps, min_samples)
        print(f"Current best score: {best_score}")
    else:
        print("Not enough clusters or too many noise points for valid scoring")
print(f"Best silhouette score: {best_score}")
print(f"Optimal parameters: eps={best_params[0]}, min_samples={best_params[1]}")
