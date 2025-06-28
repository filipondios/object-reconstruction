import json
from pathlib import Path
from sympy import Matrix, Point3D

class BaseView:

    origin: Point3D
    vx: Point3D
    vy: Point3D
    vz: Point3D
    name: str

    def __init__(self, path: Path):
        """ Initializes Vx, Vy, Vz, O, given a path """
        camera_data = path.joinpath('camera.json')
        projection = path.joinpath('plane.bmp')

        if ((not camera_data.is_file()) or
            (not projection.is_file())):
            raise FileNotFoundError
        self.projection = projection

        with open(camera_data, 'r') as file:
            data = json.load(file)
            self.origin = Point3D(data['origin'])
            self.vx = Point3D(data['vx'])
            self.vy = Point3D(data['vy'])
            self.vz = Point3D(data['vz'])
            self.name = data['name']


    def plane_to_real(self, point: tuple[float, float]) -> Point3D:
        """ Converts a 2D point to a 3D point """
        u = self.vx * point[0]
        v = self.vz * point[1]
        return self.origin + u + v


    def real_to_plane(self, point: tuple[float, float, float]) -> tuple[float, float]:
        """ Converts a 3D point to a 2D point """
        delta = Matrix([
            point[0] - self.origin.x,
            point[1] - self.origin.y,
            point[2] - self.origin.z
        ])       
        coeffs = Matrix([
            [self.vx.x, self.vz.x],
            [self.vx.y, self.vz.y],
            [self.vx.z, self.vz.z]
        ])

        solution = coeffs.solve_least_squares(delta)
        return (solution[0], solution[1])
