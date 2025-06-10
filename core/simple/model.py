import numpy as np
import pyray as rl
from core.base_model import BaseModel
from core.simple.view import View


class Model(BaseModel):

    voxel_space: np.ndarray
    resolution: int
    bounds: tuple
    surface_points: list
    space_dimensions: tuple

    def __init__(self, path: str, resolution: int):
        super().__init__(path, View)
        self.resolution = resolution
        self.surface_points = []
        self.initial_reconstruction()
        self.refine_model()
        self.generate_surface()


    def initial_reconstruction(self, _=None):
        """ Initializes the voxel space """
        self.voxel_space = np.ones((self.resolution)*3, dtype=bool)
        self.bounds = self.calculate_world_bounds()

    
    def calculate_world_bounds(self):
        """ Calculate the bounding box that encompasses all views """
        # remember, view bounds = (minXi, minZi, maxXi, maxZi)
        bounds = list(self.views[0].bounds)

        for view in self.views[1:]:
            view_bounds = view.bounds
            bounds[0] = min(bounds[0], view_bounds[0])
            bounds[1] = min(bounds[1], view_bounds[1])
            bounds[2] = max(bounds[2], view_bounds[2])
            bounds[3] = max(bounds[3], view_bounds[3])
        
        # Returns the final box defining tuple (minX, minY, minZ, maxX, maxY, maxZ)
        return (bounds[0], bounds[2], bounds[1], bounds[3], bounds[1], bounds[3])


    def refine_model(self):
        """ Reconstructs the model directly """
        for view in self.views:
            # Merge each view voxel space with the model's
            print(f'[+] Using {view.name} to reconstruct.')
            self.project_view_to_voxels(view)


    def project_view_to_voxels(self, view: View):
        get = lambda a, b, i: a + i * (b - a) / (self.resolution - 1)
        d = view.get_view_direction()

        for i in range(self.resolution):
            for j in range(self.resolution):
                if d == 'xy':
                    wx = get(self.bounds[0], self.bounds[1], i)
                    wy = get(self.bounds[2], self.bounds[3], j)
                    if not view.is_point_inside_contour(view.real_to_plane((wx, wy, 0))):
                        self.voxel_space[i, j, :] = False
                elif d == 'xz':
                    wx = get(self.bounds[0], self.bounds[1], i)
                    wz = get(self.bounds[4], self.bounds[5], j)
                    if not view.is_point_inside_contour(view.real_to_plane((wx, 0, wz))):
                        self.voxel_space[i, :, j] = False
                elif d == 'yz':
                    wy = get(self.bounds[2], self.bounds[3], i)
                    wz = get(self.bounds[4], self.bounds[5], j)
                    if not view.is_point_inside_contour(view.real_to_plane((0, wy, wz))):
                        self.voxel_space[:, i, j] = False


    def generate_surface(self):
        self.cubes = []
        fx = lambda a, b, i: a + i * (b - a) / self.resolution
        size_x = (self.bounds[1] - self.bounds[0]) / self.resolution
        size_y = (self.bounds[3] - self.bounds[2]) / self.resolution
        size_z = (self.bounds[5] - self.bounds[4]) / self.resolution
        self.cube_size = (size_x, size_y, size_z)

        for x in range(self.resolution):
            for y in range(self.resolution):
                for z in range(self.resolution):
                    if not self.voxel_space[x, y, z]:
                        continue
                    cx = fx(self.bounds[0], self.bounds[1], x)
                    cy = fx(self.bounds[2], self.bounds[3], y)
                    cz = fx(self.bounds[4], self.bounds[5], z)
                    self.cubes.append((cx, cy, cz))


    def draw_model(self):
        size = self.cube_size
        for (cx, cy, cz) in self.cubes:
            center = rl.Vector3(cx, cz, cy)
            rl.draw_cube(center, size[0], size[1], size[2], rl.WHITE)
            rl.draw_cube_wires(center, size[0], size[1], size[2], rl.BLACK)