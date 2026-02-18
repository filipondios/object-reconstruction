from pathlib import Path
import numpy as np
from shapely.geometry import LineString, MultiLineString
from core.base_view import BaseView
from utils.geo3d import Axis


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
    

    def polygon_view_to_plane(self, axis: Axis) -> list[tuple]:
        """ converts a local view 2D coordinate polygon to a 2D coordinate 
            in a plane with a normal in the same direction than axis """
        coords = np.array(self.polygon.exterior.coords, dtype=float)
        u = coords[:, 0]
        v = coords[:, 1]

        if axis == Axis.X:
            # transformation to (y, z)
            y = self.origin[1] + u * self.vx[1] + v * self.vz[1]
            z = self.origin[2] + u * self.vx[2] + v * self.vz[2]
            return list(zip(y, z))
        if axis == Axis.Y:
            # transformation to (x, z)
            x = self.origin[0] + u * self.vx[0] + v * self.vz[0]
            z = self.origin[2] + u * self.vx[2] + v * self.vz[2]
            return list(zip(x, z))
        else:
            # transformation to (x, y)
            x = self.origin[0] + u * self.vx[0] + v * self.vz[0]
            y = self.origin[1] + u * self.vx[1] + v * self.vz[1]
            return list(zip(x, y))