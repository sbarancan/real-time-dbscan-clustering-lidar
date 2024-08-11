import pygame
import ydlidar
import numpy as np
from sklearn.cluster import DBSCAN
from utils import setup_lidar, process_lidar_data, minimum_area_rectangle

def draw_lidar_data(screen, coords, labels, scale=100):
    screen.fill((232, 240, 254))  # Background color

    for (x, y), label in zip(coords, labels):
        color = (255, 0, 0) if label == -1 else (0, 255, 0)
        pygame.draw.circle(screen, color, (int(x * scale) + 400, int(y * scale) + 300), 2)

    # Draw minimum area rectangle for each cluster
    for label in set(labels):
        if label != -1:  # Ignore noise
            cluster_coords = coords[labels == label]
            corners, area, length = minimum_area_rectangle(cluster_coords)
            if corners is not None:
                pygame.draw.polygon(screen, (255, 0, 0), [(int(x * scale) + 400, int(y * scale) + 300) for x, y in corners], 1)

    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('LiDAR Visualization with DBSCAN')

    laser = setup_lidar()
    if not (laser.initialize() and laser.turnOn()):
        print("Failed to initialize LIDAR")
        return

    print("LIDAR is initialized and scanning...")
    scan = ydlidar.LaserScan()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if laser.doProcessSimple(scan):
            xs, ys = process_lidar_data(scan)
            coords = np.column_stack([xs, ys])

            # Apply DBSCAN clustering
            db = DBSCAN(eps=0.140, min_samples=11).fit(coords)
            labels = db.labels_

            draw_lidar_data(screen, coords, labels)

    laser.turnOff()
    laser.disconnecting()
    pygame.quit()

if __name__ == "__main__":
    main()
