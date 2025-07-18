from pathlib import Path
from sympy import Line3D, Matrix
from shapely.geometry import LineString, MultiLineString
from core.base_view import BaseView
import numpy as np


class View(BaseView):

    def __init__(self, path: Path):
        super().__init__(path)


    def rasterization_segments(self, line: Line3D, step: float, bounds) -> list[tuple[float, float]]:
        """ Intersect a polygon with lines and collect the resulting segemnts """
        # Calculate the direction of the segments
        q = Matrix(line.p1)
        v = Matrix(line.direction_ratio)
        pq = Matrix(self.origin) - q
        t = pq.dot(v) / v.dot(v)
        q_prime = q + v * t
        direction = q_prime - Matrix(self.origin)

        min_x, min_z, max_x, max_z = bounds
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
                line = LineString([(x, min_z - 1e6), (x, max_z + 1e6)])
                intersection = self.polygon.intersection(line)
            
                if not intersection.is_empty:
                    if isinstance(intersection, LineString):
                        coords = list(intersection.coords)
                        segments.append((coords[0], coords[-1]))
                    elif isinstance(intersection, MultiLineString):
                        for seg in intersection.geoms:
                            coords = list(seg.coords)
                            segments.append((coords[0], coords[-1]))
        return segments