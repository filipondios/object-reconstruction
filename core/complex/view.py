from pathlib import Path
from sympy import Line3D, Matrix
from shapely.geometry import Polygon, LineString, MultiLineString
from core.base_view import BaseView
import numpy as np
import cv2


class View(BaseView):

    polygon: Polygon

    def __init__(self, path: Path):
        super().__init__(path)

        # Get the object contour lines
        projection = path.joinpath('plane.bmp')
        img = cv2.imread(projection, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img, 254, 255, cv2.THRESH_BINARY_INV)
        laplacian = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]])
        img = cv2.filter2D(img, -1, laplacian)

        # Get the vertices from the contour lines
        vertices = np.array(self.get_contour_polygon(img))
        vertices[:, 1] = -vertices[:, 1]
        x_min, y_min = np.min(vertices, axis=0)
        x_max, y_max = np.max(vertices, axis=0)
        center = np.array([(x_min + x_max)/2, (y_min + y_max)/2])
        vertices_centered = vertices - center
        self.polygon = Polygon(vertices_centered)


    def get_contour_polygon(self, img: np.ndarray):
        height, width = img.shape
        initial_x = -1
        initial_z = -1
        points = []

        # Get the first contour point
        found = False
        for z in range(1, height - 1):
            for x in range(1, width - 1):
                if img[z, x] == 0xff:
                    initial_x = x
                    initial_z = z
                    found = True
                    break
            if found: break

        # Iterate through the pixel line
        directions = [(1,0),(0,1),(-1,0),(0,-1)]
        previous_x = initial_x
        previous_z = initial_z
        current_x = initial_x
        current_z = initial_z

        while True:
            # Verify if the current pixel is a vertex.
            horz = img[current_z, current_x - 1] | img[current_z, current_x + 1]
            vert = img[current_z - 1, current_x] | img[current_z + 1, current_x]

            if horz == 0xff and vert == 0xff:
                # Vertex found (x, z)
                points.append((current_x, current_z))

            for dx, dz in directions:
                next_x = current_x + dx
                next_z = current_z + dz

                if ((img[next_z, next_x] == 0xff) and
                    (next_x != previous_x or next_z != previous_z)):
                    previous_x = current_x
                    previous_z = current_z
                    current_x = next_x
                    current_z = next_z
                    break

            if current_x == initial_x and current_z == initial_z:
                # Stop when returning to the initial point
                break
        return points
    
    
    def rasterization_segments(self, line: Line3D, step: float):
        # Calculate the direction of the segments
        q = Matrix(line.p1)
        v = Matrix(line.direction_ratio)
        pq = Matrix(self.origin) - q
        t = pq.dot(v) / v.dot(v)
        q_prime = q + v * t
        direction = q_prime - Matrix(self.origin)

        min_x, min_z, max_x, max_z = self.polygon.bounds
        segments = []
        
        if direction.cross(Matrix(self.vx)).norm() <= 1e-6:
            # In this case the segments are horizontal
            for z in np.arange(min_z, max_z + step, step):
                line = LineString([(min_x - 1e6, z), (max_x + 1e6, z)])
                intersection = self.polygon.intersection(line)
                
                if not intersection.is_empty:
                    if isinstance(intersection, LineString):
                        coords = list(intersection.coords)
                        segments.append((coords[0], coords[-1]))
                    elif isinstance(intersection, MultiLineString):
                        for seg in intersection.geoms:
                            coords = list(seg.coords)
                            segments.append((coords[0], coords[-1]))

        elif direction.cross(Matrix(self.vz)).norm() <= 1e-6:
            # In this case the segments are vertical
            for x in np.arange(min_x, max_x + step, step):
                v_line = LineString([(x, min_z - 1e6), (x, max_z + 1e6)])
                intersection = self.polygon.intersection(v_line)
            
                if not intersection.is_empty:
                    if isinstance(intersection, LineString):
                        coords = list(intersection.coords)
                        segments.append((coords[0], coords[-1]))
                    elif isinstance(intersection, MultiLineString):
                        for seg in intersection.geoms:
                            coords = list(seg.coords)
                            segments.append((coords[0], coords[-1]))
        return segments