from pathlib import Path
from shapely.geometry import Point
from core.base_view import BaseView
from sympy import Matrix
from enum import Enum


class DirectionPlane(Enum):
    XZ = 0x0
    XY = 0x1
    YZ = 0x2


class View(BaseView):

    def __init__(self, path: Path):
        super().__init__(path)


    def is_point_inside_contour(self, point_2d):
        """ Checks if a point is inside the polygon """
        point = Point(point_2d)
        return self.polygon.covers(point)
    

    def get_view_direction(self):
        """ Return the axis of the space aligned with Vy """
        vy = Matrix([self.vy.x, self.vy.y, self.vy.z])
        axes = { 'x': Matrix([1,0,0]), 'y': Matrix([0,1,0]), 'z': Matrix([0,0,1]) }
        dot_products = { k: abs(vy.dot(v)) for k, v in axes.items() }
        axis = max(dot_products, key=dot_products.get)
        return { 
            'x': DirectionPlane.YZ,
            'y': DirectionPlane.XZ,
            'z': DirectionPlane.XY,
        }[axis]
