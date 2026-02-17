from sympy import Plane, Matrix, Line3D, Point3D
from shapely import Polygon
import pyray as rl
from core.base_model import BaseModel
from algorithms.complex.view import View
from enum import Enum


class Axis(Enum):
    Null = 0x0
    X = 0x1
    Y = 0x2
    Z = 0x3


class Model(BaseModel):

    planes: dict[float, tuple[Plane, list[list[Point3D]]]]

    def __init__(self, path: str, print_info: bool, step: float):
        self.planes = {}
        self.edges = []
        self.step = step
        self.planes_normal = Axis.Null
        super().__init__(path, print_info, View)


    def initial_reconstruction(self) -> None:
        if len(self.views) < 2:
            return

        view1 = self.views[0]
        vy1 = Matrix(view1.vy)
        view2_index, view2 = next(
            ((i, view) for i, view in enumerate(self.views[1:], start=1)
            if Matrix(view.vy).cross(vy1).norm() > 1e-6), (None, None))
               
        if view2 is None:
            return

        # Find the common line between views
        plane1 = Plane(view1.origin, view1.vy)
        plane2 = Plane(view2.origin, view2.vy)
        common_line = plane1.intersection(plane2)[0]

        # Calculate both views rasterization lines
        bounds1 = view1.polygon.bounds
        bounds2 = view2.polygon.bounds
        min_x = min(bounds1[0], bounds2[0])
        min_z = min(bounds1[1], bounds2[1])
        max_x = max(bounds1[2], bounds2[2])
        max_z = max(bounds1[3], bounds2[3])
        bounds = (min_x, min_z, max_x, max_z)

        segments1 = view1.rasterization_segments(common_line, self.step, bounds)
        segments2 = view2.rasterization_segments(common_line, self.step, bounds)
        print(f'[+] Using {view1.name} and {view2.name} for initial reconstruction.')

        # Calculate the axis aligned with the common line
        axis_direction = tuple(Matrix(common_line.direction).normalized().__abs__())
        axes = {(1,0,0): Axis.X, (0,1,0): Axis.Y, (0,0,1): Axis.Z}
        axis = axes[axis_direction]       

        for segment1 in segments1:
            # contour generation lines for segment1
            src1 = view1.plane_to_real(segment1[0])
            dst1 = view1.plane_to_real(segment1[1])
            
            contourv1_1 = Line3D(src1, direction_ratio=view1.vy)
            contourv1_2 = Line3D(dst1, direction_ratio=view1.vy)

            plane = Plane(src1, common_line.direction)
            if axis == Axis.X: key = src1.x
            elif axis == Axis.Y: key = src1.y
            elif axis == Axis.Z: key = src1.z

            if key not in self.planes:
                plane = Plane(src1, common_line.direction)
                self.planes[key] = (plane, [])
            polygon_list = self.planes[key][1]

            for segment2 in segments2:
                src2 = view2.plane_to_real(segment2[0])

                if src2 not in plane:
                    continue

                # contour generation lines for segment1
                dst2 = view2.plane_to_real(segment2[1])
                contourv2_1 = Line3D(src2, direction_ratio=view2.vy)
                contourv2_2 = Line3D(dst2, direction_ratio=view2.vy)
               
                polygon_list.append([
                    contourv1_1.intersect(contourv2_1).args[0],
                    contourv1_1.intersect(contourv2_2).args[0],
                    contourv1_2.intersect(contourv2_2).args[0],
                    contourv1_2.intersect(contourv2_1).args[0]
                ])

        self.views.pop(view2_index)
        self.views.pop(0)


    def refine_model(self) -> None:
        """ Reconstructs the model directly """
        _, (first_plane, _) = next(iter(self.planes.items()))
        normal = Matrix(first_plane.normal_vector)
        
        # Get aligned axis
        if abs(normal[0]) > 0.99: 
            plane_axis = Axis.X
        elif abs(normal[1]) > 0.99:
            plane_axis = Axis.Y
        else: plane_axis = Axis.Z

        for view in self.views:
            # Ensure the actual view's line of vission is aligned with
            # all the planes' normal, in order to ensure a full non-
            # empty polygon intersections.
            if Matrix(view.vy).cross(normal).norm() > 1e-6:
                continue
            
            # convert view's 2D polygon to 3D
            print(f'[+] Using {view.name} to refine.')            
            view_polygon_3d = [view.plane_to_real(coord) 
                            for coord in view.polygon.exterior.coords[:-1]]
            
            for (key, (plane, polygons)) in self.planes.items():
                # project the view's polygon into the plane
                refined_polygons = []
                view_poly_projected = [plane.projection(point) 
                    for point in view_polygon_3d]
                
                for polygon3d in polygons:
                    # 3D coplanar intersection
                    intersection_3d = self.intersect_3dpolygons(
                        polygon3d, view_poly_projected, plane_axis)

                    if intersection_3d: # if not empty, add
                        refined_polygons.append(intersection_3d)
                self.planes[key] = (plane, refined_polygons)


    def intersect_3dpolygons(self, poly1: list[Point3D], poly2: list[Point3D], axis: Axis) -> list[Point3D]:
        """ Intersect two coplanar 3d polygons, resulting in another polygon or empty set.
            Intersecting two coplanar 3d polygons that are contained in a plane parallel to
            one of the coordinate system plates (XY, XZ, YZ), can be done like a 2d polygon
            intersection ignoring the constant axis """
        
        if axis == Axis.X:
            poly1_2d = [(p.y, p.z) for p in poly1]
            poly2_2d = [(p.y, p.z) for p in poly2]
            fixed = poly1[0].x
        
        elif axis == Axis.Y:
            poly1_2d = [(p.x, p.z) for p in poly1]
            poly2_2d = [(p.x, p.z) for p in poly2]
            fixed = poly1[0].y

        else: # axis == Axis.Z:
            poly1_2d = [(p.x, p.y) for p in poly1]
            poly2_2d = [(p.x, p.y) for p in poly2]
            fixed = poly1[0].z

        # calculate 2d intersection
        poly1_2d = Polygon(poly1_2d)
        poly2_2d = Polygon(poly2_2d)
        intersection = poly1_2d.intersection(poly2_2d)

        if intersection.is_empty or not isinstance(intersection, Polygon):
            return []
        result3d = []

        for v in intersection.exterior.coords:
            if axis == Axis.X:   result3d.append(Point3D(fixed, v[0], v[1]))
            elif axis == Axis.Y: result3d.append(Point3D(v[0], fixed, v[1]))
            else: result3d.append(Point3D(v[0], v[1], fixed))
        return result3d


    def draw_model(self) -> None:
        for (_, polygons) in self.planes.values():
            for poly in polygons:
                for i in range(len(poly)):
                    a = poly[i]
                    b = poly[(i + 1) % len(poly)]
                    va = rl.Vector3(a[0], a[2], a[1])
                    vb = rl.Vector3(b[0], b[2], b[1])
                    rl.draw_line_3d(va, vb, rl.WHITE)


    def additional_info(self) -> None:
        planes = len(self.planes)
        polygons = 0
        vertices = 0

        for _, (_, poly_list) in self.planes.items():
            polygons += len(poly_list)
            for polygon in poly_list:
                vertices += len(polygon)

        info = (f"[+] Model additional information:\n"
            f"Model bounds: {self.bounds}\n"
            f"Number of planes: {planes}\n"
            f"Number of polygons: {polygons}\n"
            f"Number of vertices: {vertices}\n")
        print(info)
