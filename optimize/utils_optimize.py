import os
import ydlidar
import time
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, box


def save_lidar_data(laser, duration=60, file_path="C:/lidar_data/data.csv"):
    try:
        if not laser.initialize() or not laser.turnOn():
            print("Failed to initialize LIDAR")
            return

        print("LIDAR is initialized and scanning...")
        scan = ydlidar.LaserScan()
        start_time = time.time()

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode='a', newline='') as file:  # Append mode
            writer = csv.writer(file)
            scan_frequency = laser.getlidaropt_toFloat(ydlidar.LidarPropScanFrequency)
            if isinstance(scan_frequency, list):
                scan_frequency = scan_frequency[0]
            sleep_duration = 1.0 / scan_frequency
            print(f"Scan frequency: {scan_frequency} Hz, Sleep duration: {sleep_duration} seconds")

            collected_rows = 0
            while time.time() - start_time < duration:
                if laser.doProcessSimple(scan):
                    timestamp = int(scan.stamp)
                    scan_data = [timestamp]
                    for point in scan.points:
                        scan_data.extend([point.angle, point.range, point.intensity])
                    writer.writerow(scan_data)
                    collected_rows += 1
                else:
                    print("Failed to get Lidar Data")
                time.sleep(sleep_duration)

            print(f"Total rows collected: {collected_rows}")

        print(f"LIDAR data saved to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        laser.turnOff()
        laser.disconnecting()



def read_lidar_data(file_path):
    """Reads LiDAR data from a CSV file."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = [line.strip().split(',') for line in lines]
    return data


def plot_lidar_data(rectangular_coords, interval=1000):
    """Plots LiDAR data as blue dots with a 20-second animation."""
    fig, ax = plt.subplots()
    scat = ax.scatter([], [], s=1, color='blue')

    def init():
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        return scat,

    def update(frame):
        if frame < len(rectangular_coords):
            x_data = [point[0] for point in rectangular_coords[frame]]
            y_data = [point[1] for point in rectangular_coords[frame]]
            scat.set_offsets(np.c_[x_data, y_data])
        return scat,

    ani = animation.FuncAnimation(fig, update, frames=len(rectangular_coords), init_func=init, interval=interval, blit=True)
    plt.show()
    


def convert_lidar_data_to_rectangular(data):
    """Converts LiDAR data from polar to rectangular coordinates."""
    rectangular_coords = []
    for row in data:
        coords = []
        for i in range(1, len(row), 3):
            try:
                angle = float(row[i])
                range_ = float(row[i+1])
                x, y = polar_to_rectangular(angle, range_)
                coords.append((x, y))
            except (ValueError, IndexError):
                # Skip invalid data or incomplete entries
                continue
        rectangular_coords.append(coords)
    return rectangular_coords


def polar_to_rectangular(angle, range_):
    """Converts polar coordinates to rectangular coordinates assuming angles are in degrees."""
    x = range_ * np.cos(angle)
    y = range_ * np.sin(angle)
    return x, y



# simple efficient rectangle fitting for real time
def minimum_area_rectangle(points):
    """Find the minimum area rectangle from a set of points."""
    if len(points) < 3:  # Not enough points to form a rectangle
        return None, None, None

    hull_points = points[ConvexHull(points).vertices]
    hull_polygon = Polygon(hull_points)
    min_area_rect = hull_polygon.minimum_rotated_rectangle

    # Extract the corner points of the rectangle
    x, y = min_area_rect.exterior.coords.xy
    corners = np.column_stack((x, y))
    return corners[:-1], min_area_rect.area, min_area_rect.length