from sympy import Point3D, Matrix, Line3D
from core.base_model import BaseModel
from core.simple.view import View
import pyray as rl


class Model(BaseModel):

    vertices: list[Point3D]
    edges: list[Point3D, Point3D]

    def __init__(self, path: str):
        super().__init__(path, View)
        self.views = sorted(self.views, key=lambda v: len(v.vertices), reverse=True)
        self.vertices = []
        self.edges = []
        print('[+] Starting initial reconstruction')
        self.initial_reconstruction()
        print('[+] Refining model')
        self.refine_model()
        print('[+] Generating edges.')
        self.generate_edges()


    def initial_reconstruction(self, args=None):
        if len(self.views) < 2:
            return

        view1 = self.views[0]
        vy1 = Matrix(view1.vy)
        view2 = next((view for view in self.views[1:]
            if Matrix(view.vy).cross(vy1).norm() > 1e-6), None)
        
        if view2 is None:
            return
        
        print('[+] Using ' + view1.name + ' and ' + view2.name 
              + ' for initial reconstruction.')

        for vertex1 in view1.vertices:
            # Try to intersect pairs of view vertex lines
            vertex1 = view1.plane_to_real(vertex1)
            line1 = Line3D(vertex1, direction_ratio=view1.vy)

            for vertex2 in view2.vertices:
                vertex2 = view2.plane_to_real(vertex2)
                line2 = Line3D(vertex2, direction_ratio=view2.vy)
                intersection = line1.intersect(line2)
                
                if not intersection.is_empty:
                    self.vertices.append(intersection.args[0])


    def refine_model(self):
        for view in self.views[2:]:
            print('[+] Using ' + view.name + ' to refine.')
            to_remove = []

            for (index, vertex) in enumerate(self.vertices):
                # Project the vertex into the view
                point = view.real_to_plane(vertex)
                point = view.plane_to_image(point)

                # See if the corresponding pixel in the image plane
                # is a background pixel (white)
                if view.projection[point[1], point[0]] == 0xff:
                    to_remove.append(index)

            for index in reversed(to_remove):
                del self.vertices[index]


    def generate_edges(self):
        x_axis = Point3D(1,0,0)
        y_axis = Point3D(0,1,0)
        z_axis = Point3D(0,0,1)

        for vertex in self.vertices:
            # Calculate a minumun distance vertex to the actual in
            # all of the directions (x, y, z).
            x_line = Line3D(vertex, direction_ratio=x_axis)
            y_line = Line3D(vertex, direction_ratio=y_axis)
            z_line = Line3D(vertex, direction_ratio=z_axis)
            min_x = None
            min_y = None
            min_z = None

            for other in self.vertices:
                if other == vertex:
                    continue

                if (x_line.contains(other) and (other.x > vertex.x
                    and (min_x is None or other.x < min_x.x))):
                    min_x = other

                if (y_line.contains(other) and (other.y > vertex.y
                    and (min_y is None or other.y < min_y.y))):
                    min_y = other

                if (z_line.contains(other) and (other.z > vertex.z
                    and (min_z is None or other.z < min_z.z))):
                    min_z = other

            # Not all minimum distance vertices form an edge with
            # the current vertex in the real model.
            if self.is_valid_edge(vertex, min_x, x_axis): 
                self.edges.append((vertex, min_x))

            if self.is_valid_edge(vertex, min_y, y_axis): 
                self.edges.append((vertex, min_y))

            if self.is_valid_edge(vertex, min_z, z_axis): 
                self.edges.append((vertex, min_z))


    def is_valid_edge(self, src: Point3D, dst: Point3D, axis: Point3D) -> bool:
        # Return false if the projection of the first point of the line between
        # both points is a background pixel (white) is some view.

        if dst is None: return False
        next = src + axis

        for view in self.views:
            projected = view.real_to_plane(next)
            point = view.plane_to_image(projected)
            pixel = view.projection[point[1], point[0]]
            if pixel == 0xff: return False            
        return True


    def drawModel(self):
        for (src, dst) in self.edges:
            vsrc = rl.Vector3(src[0], src[2], src[1])
            vdst = rl.Vector3(dst[0], dst[2], dst[1])
            rl.draw_line_3d(vsrc, vdst, rl.WHITE)