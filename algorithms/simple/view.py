import numpy as np
from shapely.geometry import Point
from core.base_view import BaseView
from utils.geo3d import Plane


class View(BaseView):

    def is_point_inside_contour(self, point_2d):
        """ Checks if a point is inside the polygon """
        point = Point(point_2d)
        return self.polygon.covers(point)
    

    def get_view_direction(self):
        """ Return the axis of the space aligned with Vy """
        axes = {
            'x': np.array([1, 0, 0], dtype=float),
            'y': np.array([0, 1, 0], dtype=float),
            'z': np.array([0, 0, 1], dtype=float),
        }

        dot_products = {k: abs(np.dot(self.vy, v)) for k, v in axes.items()}
        axis = max(dot_products, key=dot_products.get)
        return { 'x': Plane.YZ, 'y': Plane.XZ, 'z': Plane.XY }[axis]
