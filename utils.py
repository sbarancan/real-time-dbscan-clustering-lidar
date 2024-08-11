import ydlidar
import numpy as np
import pygame
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, box



def setup_lidar(baudrate=230400, port="COM3", Freq=7.0, SampleRate=5, SingleChannel=False):
    ydlidar.os_init()
    ports = ydlidar.lidarPortList()
    port = "COM5"  # Adjust for your system, Windows might be COM3, etc.
    for key, value in ports.items():
        port = value
        print(port)
    laser = ydlidar.CYdLidar()
    laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
    laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, baudrate)
    laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
    laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
    laser.setlidaropt(ydlidar.LidarPropScanFrequency, Freq)
    laser.setlidaropt(ydlidar.LidarPropSampleRate, SampleRate)
    laser.setlidaropt(ydlidar.LidarPropSingleChannel, SingleChannel)
    laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0)
    laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0)
    laser.setlidaropt(ydlidar.LidarPropMaxRange, 16.0)
    laser.setlidaropt(ydlidar.LidarPropMinRange, 0.08)
    laser.setlidaropt(ydlidar.LidarPropIntenstiy, False)
    return laser


def read_lidar_data(laser, scan):
    return laser.doProcessSimple(scan)


def process_lidar_data(scan, min_intensity=0, min_range=0.1, max_range=16.0):
    angles = np.array([point.angle for point in scan.points])
    ranges = np.array([point.range for point in scan.points])
    intensities = np.array([point.intensity for point in scan.points])
    
    valid_indices = (intensities >= min_intensity) & (ranges >= min_range) & (ranges <= max_range)
    filtered_angles = angles[valid_indices]
    filtered_ranges = ranges[valid_indices]
    
    xs = filtered_ranges * np.cos(filtered_angles)
    ys = filtered_ranges * np.sin(filtered_angles)
    return xs, ys

def update_plot(frame, laser, scan, scatter):
    if read_lidar_data(laser, scan):
        xs, ys = process_lidar_data(scan)
        scatter.set_offsets(np.column_stack([xs, ys]))
    return scatter,


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

        


def draw_covariance_ellipse(screen, mean, cov, n_std=3.0, color=(0, 0, 255), scale=100):
    """
    Draw an ellipse representing the covariance matrix on a Pygame surface.
    """
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    order = eigenvalues.argsort()[::-1]
    eigenvalues, eigenvectors = eigenvalues[order], eigenvectors[:, order]

    angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1])) # in degrees
    width, height = 2 * n_std * np.sqrt(eigenvalues)

    # Convert from numpy to Pygame coordinates
    pos = (int(mean[0] * scale) + 400, int(mean[1] * scale) + 300)
    size = (int(width * scale), int(height * scale))

    ellipse_surface = pygame.Surface((size[0] * 2, size[1] * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(ellipse_surface, color, ellipse_surface.get_rect(), 1)
    ellipse_surface = pygame.transform.rotate(ellipse_surface, -angle)

    # Blit the rotated ellipse onto the screen
    screen.blit(ellipse_surface, ellipse_surface.get_rect(center=pos))

        