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
        _, (plane, _) = next(iter(self.planes.items()))
        planes_normal = Matrix(plane.normal_vector)
        
        for view in self.views:
            # Ensure the actual view's line of vission is aligned with
            # all the planes' normal, in order to ensure a full non-
            # empty polygon intersections.
            
            if Matrix(view.vy).cross(planes_normal).norm() > 1e-6:
                continue
   
            print(f'[+] Using {view.name} to refine.')
            for (key, (plane, polygons)) in self.planes.items():
                refined_polygons = []

                for polygon3d in polygons:
                    # Project and refine the current polygon via intersection
                    projection = Polygon([view.real_to_plane(point) for point in polygon3d])
                    intersection = view.polygon.intersection(projection)

                    if intersection.is_empty or not isinstance(intersection, Polygon):
                        continue # Discard polygon from list

                    projection = [plane.projection(view.plane_to_real(point))
                        for point in intersection.exterior.coords]
                    refined_polygons.append(projection)
                self.planes[key] = (plane, refined_polygons)


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
