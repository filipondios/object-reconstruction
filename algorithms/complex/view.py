from pathlib import Path
from shapely.geometry import LineString, MultiLineString
import numpy as np
from core.base_view import BaseView


class View(BaseView):

    def __init__(self, path: Path):
        super().__init__(path)


    def rasterization_segments(self, line_point, line_dir, step: float, bounds) -> list[tuple]:
        """ Intersect a polygon with lines and collect the resulting segemnts """
        # project the common line onto the view to get segment direction
        pq = self.origin - line_point
        t = np.dot(pq, line_dir) / np.dot(line_dir, line_dir)
        q_prime = line_point + line_dir * t
        direction = q_prime - self.origin

        # is the segment direction parallel to vx or vz?
        cross_with_vx = np.cross(direction, self.vx)
        cross_with_vz = np.cross(direction, self.vz)

        min_x, min_z, max_x, max_z = bounds
        segments = []

        if np.linalg.norm(cross_with_vx) <= 1e-6:
            # segments are horizontal (parallel to vx -> sweep over z)
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

        elif np.linalg.norm(cross_with_vz) <= 1e-6:
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