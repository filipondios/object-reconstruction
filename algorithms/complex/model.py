import pyray as rl
import numpy as np
from shapely import Polygon
from algorithms.complex.view import View
from core.base_model import BaseModel
import utils.geo3d as geo3d


class Model(BaseModel):

    """ basically [key] -> (plane_point, plane_normal, polygons_in_plane) """
    planes: dict[float, tuple[np.ndarray, np.ndarray, list[list[np.ndarray]]]]

    def __init__(self, path: str, step: float):
        self.planes = {}
        self.edges = []
        self.step = step
        self.planes_normal = geo3d.Axis.Null
        super().__init__(path, View)


    def initial_reconstruction(self):
        if len(self.views) < 2:
            return

        view1 = self.views[0]
        vy1 = view1.vy

        # find another non-aligned view
        view2_index, view2 = next(
            ((i, v) for i, v in enumerate(self.views[1:], start=1)
            if np.linalg.norm(np.cross(v.vy, vy1)) > 1e-6), 
            (None, None))
               
        if view2 is None:
            return

        # Find the common line between views
        line_point, line_dir = geo3d.planes_intersection(
            view1.vy, view1.origin,
            view2.vy, view2.origin)
        line_dir = line_dir / np.linalg.norm(line_dir)
        
        # Calculate both views rasterization lines
        bounds1 = view1.polygon.bounds
        bounds2 = view2.polygon.bounds
        min_x = min(bounds1[0], bounds2[0])
        min_z = min(bounds1[1], bounds2[1])
        max_x = max(bounds1[2], bounds2[2])
        max_z = max(bounds1[3], bounds2[3])
        bounds = (min_x, min_z, max_x, max_z)

        segments1 = view1.rasterization_segments(line_point, line_dir, self.step, bounds)
        segments2 = view2.rasterization_segments(line_point, line_dir, self.step, bounds)

        # Calculate the axis aligned with the common line
        abs_dir = np.abs(line_dir)
        axis_idx = int(np.argmax(abs_dir))

        # direction vectors
        d1 = view1.vy
        d2 = view2.vz
        plane_normal = line_dir

        # pregroup segments by their axis-aligned
        segments2_dict: dict[float, list] = {}
        for seg in segments2:
            src = view2.plane_to_real(seg[0])
            dst = view2.plane_to_real(seg[1])
            key = round(float(src[axis_idx]), 6)
            segments2_dict.setdefault(key, []).append((src, dst))

        for segment1 in segments1:
            # get segment1 end points
            src1 = view1.plane_to_real(segment1[0])
            dst1 = view1.plane_to_real(segment1[1])
            key = round(float(src1[axis_idx]), 6)

            if key not in self.planes:
                self.planes[key] = (src1, plane_normal, [])

            # get poly list and coplanar segments2
            polygon_list = self.planes[key][2]
            matching = segments2_dict.get(key, [])

            for (src2, dst2) in matching:
                polygon_list.append([
                    geo3d.intersect_lines(src1, d1, src2, d2),
                    geo3d.intersect_lines(src1, d1, dst2, d2),
                    geo3d.intersect_lines(dst1, d1, dst2, d2),
                    geo3d.intersect_lines(dst1, d1, src2, d2),
                ])

        # delete used views
        self.views.pop(view2_index)
        self.views.pop(0)
        return self


    def refine_model(self):
        """ Reconstructs the model directly """
        if not self.planes:
            return

        # get aligned axis from the model's plane normal
        _, (_, first_normal, _) = next(iter(self.planes.items()))
        axis_index = int(np.argmax(np.abs(first_normal)))
        plane_axis = [geo3d.Axis.X, geo3d.Axis.Y, geo3d.Axis.Z][axis_index]

        for view in self.views:
            # ensure alignment between the view's direction and the planes
            if np.linalg.norm(np.cross(view.vy, first_normal)) > 1e-6: continue
            poly_view_transform = Polygon(view.polygon_view_to_plane(plane_axis))

            for (key, (plane_point, plane_normal, polygons)) in self.planes.items():
                refined_polygons = []
                for polygon3d in polygons:
                    # 3D coplanar intersection between polygons
                    intersection_3d = geo3d.intersect_3dpolygons(
                        polygon3d, poly_view_transform, plane_axis)

                    if intersection_3d: # if not empty, add
                        refined_polygons.append(intersection_3d)
                self.planes[key] = (plane_point, plane_normal, refined_polygons)
        return self


    def draw_model(self):
        for (_, _, polygons) in self.planes.values():
            for poly in polygons:
                for i in range(len(poly)):
                    a = poly[i]
                    b = poly[(i + 1) % len(poly)]
                    va = rl.Vector3(a[0], a[2], a[1])
                    vb = rl.Vector3(b[0], b[2], b[1])
                    rl.draw_line_3d(va, vb, rl.WHITE)


    def additional_info(self):
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
