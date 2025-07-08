import json
from pathlib import Path
from sympy import Matrix, Point3D
from shapely.geometry import Polygon
import numpy as np
import cv2


class BaseView:

    origin: Point3D
    vx: Point3D
    vy: Point3D
    vz: Point3D
    name: str
    polygon: Polygon

    def __init__(self, path: Path):
        """ Initializes Vx, Vy, Vz, O, given a path """
        camera_data = path.joinpath('camera.json')
        projection = path.joinpath('plane.bmp')

        if ((not camera_data.is_file()) or
            (not projection.is_file())):
            raise FileNotFoundError

        with open(camera_data, 'r') as file:
            data = json.load(file)
            self.origin = Point3D(data['origin'])
            self.vx = Point3D(data['vx'])
            self.vy = Point3D(data['vy'])
            self.vz = Point3D(data['vz'])
            self.name = data['name']

        # Get the  object's projection contour lines
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

    
    def get_contour_polygon(self, img: np.ndarray) -> list[tuple[int, int]]:
        """ Iterates over a closed line in a image and returns the
            vertices that describe such polygon's line. """

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


    def plane_to_real(self, point: tuple[float, float]) -> Point3D:
        """ Converts a 2D point to a 3D point """
        u = self.vx * point[0]
        v = self.vz * point[1]
        return self.origin + u + v


    def real_to_plane(self, point: tuple[float, float, float]) -> tuple[float, float]:
        """ Converts a 3D point to a 2D point """
        delta = Matrix([
            point[0] - self.origin.x,
            point[1] - self.origin.y,
            point[2] - self.origin.z
        ])       
        coeffs = Matrix([
            [self.vx.x, self.vz.x],
            [self.vx.y, self.vz.y],
            [self.vx.z, self.vz.z]
        ])

        solution = coeffs.solve_least_squares(delta)
        return (solution[0], solution[1])
