from pathlib import Path
from shapely.geometry import Point
from core.complex.view import View as ComplexView
import numpy as np
from sympy import Matrix


class View(ComplexView):

    bounds: tuple

    def __init__(self, path: Path):
        super().__init__(path)
        min_x, min_y, max_x, max_y = self.polygon.bounds
        self.bounds = (min_x, min_y, max_x, max_y)


    def is_point_inside_contour(self, point_2d):
        """ Checks if a point is inside the polygon """
        point = Point(point_2d)
        return self.polygon.covers(point)


    def get_view_direction(self):
        """ Return the axis of the space aligned with Vy """
        vy = Matrix([self.vy.x, self.vy.y, self.vy.z])
        axes = {'x': Matrix([1,0,0]), 'y': Matrix([0,1,0]), 'z': Matrix([0,0,1])}
        dot_products = {k: abs(vy.dot(v)) for k, v in axes.items()}
        axis = max(dot_products, key=dot_products.get)
        return { 'x': 'yz', 'y': 'xz', 'z': 'xy' }[axis]


    def project_to_voxel_space(self, voxel_bounds, resolution):
        """Transform contour points to voxel space coordinates"""
        # Map from world coordinates to voxel indices
        world_min = np.array([voxel_bounds[0], voxel_bounds[2]])
        world_max = np.array([voxel_bounds[1], voxel_bounds[3]])
        scale = (resolution - 1) / (world_max - world_min)
        return ((self.contour_points - world_min) * scale).astype(int)