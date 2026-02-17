import json
from pathlib import Path
from sympy import Point3D
from shapely.geometry import Polygon
import numpy as np
import cv2


class BaseView:

    origin: np.ndarray
    vx: np.ndarray
    vy: np.ndarray
    vz: np.ndarray
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
            self.origin = np.array(data['origin'], dtype=float)
            self.vx = np.array(data['vx'], dtype=float)
            self.vy = np.array(data['vy'], dtype=float)
            self.vz = np.array(data['vz'], dtype=float)
            self.name = data['name']

        # Get the  object's projection contour lines
        img = cv2.imread(projection, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img, 254, 255, cv2.THRESH_BINARY_INV)
        laplacian = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]])
        img = cv2.filter2D(img, -1, laplacian) 

        # Get the vertices from the contour lines
        vertices = np.array(self.get_contour_polygon(img), dtype=float)
        min_vals, max_vals = np.min(vertices, axis=0), np.max(vertices, axis=0)
        center = (min_vals + max_vals) / 2
        self.polygon = Polygon(vertices - center)

        # calculate view inverse transform matrix
        transform_matrix = np.array([
            [self.vx[0], self.vz[0]],
            [self.vx[1], self.vz[1]],
            [self.vx[2], self.vz[2]]], dtype=float)
        self.transform_inv = np.linalg.pinv(transform_matrix)

    
    def get_contour_polygon(self, img: np.ndarray) -> list[tuple[int, int]]:
        """ Iterates over a closed line in a image and returns the
            vertices that describe such polygon's line. """
        
        height, width = img.shape
        start = next(((x, z) for z in range(1, height - 1) 
            for x in range(1, width - 1) if img[z, x] == 0xff), None)

        # Iterate through the pixel line
        directions = [(1,0),(0,1),(-1,0),(0,-1)]
        ix, iz = start
        px, pz = ix, iz # previous pixel
        cx, cz = ix, iz # current pixel
        points = []

        while True:
            # Verify if the current pixel is a vertex.
            horz = img[cz, cx - 1] | img[cz, cx + 1]
            vert = img[cz - 1, cx] | img[cz + 1, cx]

            if horz == 0xff and vert == 0xff:
                # Vertex found (x, z)
                points.append((cx, -cz))

            for dx, dz in directions:
                nx = cx + dx
                nz = cz + dz

                if ((img[nz, nx] == 0xff) and
                    (nx != px or nz != pz)):
                    px, pz = cx, cz
                    cx, cz = nx, nz
                    break

            if cx == ix and cz == iz:
                break
        return points


    def plane_to_real(self, point: np.ndarray) -> np.ndarray:
        """ Converts a 2D point to a 3D point """
        u = self.vx * point[0]
        v = self.vz * point[1]
        return self.origin + u + v


    def real_to_plane(self, point: np.ndarray) -> np.ndarray:
        """ Converts a 3D point to a 2D point """
        delta = point - self.origin        
        solution = self.transform_inv @ delta
        return np.array([solution[0], solution[1]])
