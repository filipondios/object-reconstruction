from sympy import Plane, Matrix, Line3D, Point3D
from shapely import Polygon
import pyray as rl
from core.base_model import BaseModel
from core.complex.view import View


class Model(BaseModel):

    planes: dict[Plane, list[list[Point3D]]]

    def __init__(self, path: str, step: float):
        super().__init__(path, View)
        self.planes = {}
        print('[+] Starting initial reconstruction')
        self.initial_reconstruction(step)
        print('[+] Refining model')
        self.refine_model()


    def initial_reconstruction(self, step: float):
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
        segments1 = view1.rasterization_segments(common_line, step)
        segments2 = view2.rasterization_segments(common_line, step)
        print('[+] Using ' + view1.name + ' and ' + view2.name + ' for initial reconstruction.')

        for segment1 in segments1:
            # contour generation lines for segment1
            src1 = view1.plane_to_real(segment1[0])
            dst1 = view1.plane_to_real(segment1[1])
            
            contourv1_1 = Line3D(src1, direction_ratio=view1.vy)
            contourv1_2 = Line3D(dst1, direction_ratio=view1.vy)

            plane = Plane(src1, common_line.direction)
            polygon_list = self.planes.setdefault(plane, [])

            for segment2 in segments2:
                src2 = view2.plane_to_real(segment2[0])

                if not (src2 in plane):
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


    def refine_model(self):
        for view in self.views:
            print('[+] Using ' + view.name + ' to refine.')
            for (plane, polygons) in self.planes.items():
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
                self.planes[plane] = refined_polygons


    def draw_model(self):
        for polygons in self.planes.values():
            for poly in polygons:
                for i in range(len(poly)):
                    a = poly[i]
                    b = poly[(i + 1) % len(poly)]
                    va = rl.Vector3(a[0], a[2], a[1])
                    vb = rl.Vector3(b[0], b[2], b[1])
                    rl.draw_line_3d(va, vb, rl.WHITE)                                                                    