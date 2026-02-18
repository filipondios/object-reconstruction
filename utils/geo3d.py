from enum import Enum
import numpy as np
from shapely import Polygon


class Axis(Enum):
    Null = 0x0
    X = 0x1
    Y = 0x2
    Z = 0x3

class Plane(Enum):
    XZ = 0x0
    XY = 0x1
    YZ = 0x2


def intersect_lines(p1, d1, p2, d2) -> np.ndarray:
    """ Intersects two 3D lines p1 + t*d1 & p2 + s*d2. """
    A = np.column_stack([d1, -d2])
    ts, _, _, _ = np.linalg.lstsq(A, p2 - p1, rcond=None)
    return p1 + ts[0] * d1


def point_on_plane(point, plane_normal, plane_point, tol= 1e-6) -> bool:
    """ Checks if a 3D point lies on a 3D plane """
    return abs(np.dot(plane_normal, point - plane_point)) < tol


def project_point_to_plane(point, plane_normal, plane_point) -> np.ndarray:
    """ Calculates the orthogonal projection of point onto plane """
    return point - np.dot(plane_normal, point - plane_point) * plane_normal


def planes_intersection(n1, p1, n2, p2) -> np.ndarray[np.ndarray, np.ndarray]:
    """ Calculate the intersection line between two planes """
    direction = np.cross(n1, n2)

    # find a point on the line, solving the 2-plane system
    i = np.argmax(np.abs(direction))
    rows = [r for r in range(3) if r != i]
    
    A = np.array([[n1[rows[0]], n1[rows[1]]],
                    [n2[rows[0]], n2[rows[1]]]], dtype=float)
    b = np.array([np.dot(n1, p1), np.dot(n2, p2)], dtype=float)

    xy = np.linalg.solve(A, b)
    point = np.zeros(3, dtype=float)
    point[rows[0]] = xy[0]
    point[rows[1]] = xy[1]
    return np.array([point, direction])


def intersect_3dpolygons(poly1, poly2, axis):
    """ Intersect two coplanar 3D polygons """
    # poly2 must be already processed to 2D here
    if axis == Axis.X:
        poly1_2d = [(p[1], p[2]) for p in poly1]
        fixed = poly1[0][0]

    elif axis == Axis.Y:
        poly1_2d = [(p[0], p[2]) for p in poly1]
        fixed = poly1[0][1]

    else: # axis == Axis.Z:
        poly1_2d = [(p[0], p[1]) for p in poly1]
        fixed = poly1[0][2]

    # calculate 2d intersection
    poly1_2d = Polygon(poly1_2d)
    intersection = poly1_2d.intersection(poly2)

    if intersection.is_empty or not isinstance(intersection, Polygon):
        return []
    result3d = []

    for v in intersection.exterior.coords:
        if axis == Axis.X:   result3d.append(np.array([fixed, v[0], v[1]], dtype=float))
        elif axis == Axis.Y: result3d.append(np.array([v[0], fixed, v[1]], dtype=float))
        else: result3d.append(np.array([v[0], v[1], fixed], dtype=float))
    return result3d