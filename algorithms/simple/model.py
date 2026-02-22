import numpy as np
import pyray as rl
from core.base_model import BaseModel
from algorithms.simple.view import View
from utils.geo3d import Plane


class Model(BaseModel):

    resolution: int
    voxel_space: np.ndarray[np.bool_]
    cubes: list[tuple[float, float, float]]
    cube_size: tuple[float, float, float]

    def __init__(self, path: str, resolution: int):
        self.resolution = resolution
        self.cubes = []
        super().__init__(path, View)


    def initial_reconstruction(self):
        """ Initializes the voxel space """
        self.voxel_space = np.ones((self.resolution,)*3, dtype=bool)
        return self


    def refine_model(self):
        """ Reconstructs the model directly """
        for view in self.views:
            # Merge each view voxel space with the model's
            self.project_view_to_voxels(view)
        return self


    def project_view_to_voxels(self, view: View) -> None:
        """ Project a 2D voxel grid onto a view, then remove those
            rows whose projection lies outside the view polygon.  """

        res = self.resolution
        get = lambda a, b, i: a + i * (b - a) / (res - 1)
        d = view.get_view_direction()
        indices = np.arange(res)

        if d == Plane.XY:
            # grid parallel to XY plane
            i_grid, j_grid = np.meshgrid(indices, indices, indexing='ij')
            wx = get(self.bounds[0], self.bounds[1], i_grid)
            wy = get(self.bounds[2], self.bounds[3], j_grid)
            wz = np.zeros_like(wx)
        
            # Vectorized conversion to 2D
            points_3d = np.stack([wx, wy, wz], axis=-1)
            points_2d = view.real_to_plane_batch(points_3d.reshape(-1, 3))
            points_2d = points_2d.reshape(res, res, 2)

            mask = view.points_inside_polygon_batch(points_2d)
            self.voxel_space &= mask[:, :, np.newaxis]

        elif d == Plane.XZ:
            # grid parallel to XZ plane
            i_grid, j_grid = np.meshgrid(indices, indices, indexing='ij')
            wx = get(self.bounds[0], self.bounds[1], i_grid)
            wz = get(self.bounds[4], self.bounds[5], j_grid)
            wy = np.zeros_like(wx)

            points_3d = np.stack([wx, wy, wz], axis=-1)
            points_2d = view.real_to_plane_batch(points_3d.reshape(-1, 3))
            points_2d = points_2d.reshape(res, res, 2)
            
            mask = view.points_inside_polygon_batch(points_2d)
            self.voxel_space &= mask[:, np.newaxis, :]
        
        elif d == Plane.YZ:
            # grid parallel to YZ plane
            i_grid, j_grid = np.meshgrid(indices, indices, indexing='ij')
            wy = get(self.bounds[2], self.bounds[3], i_grid)
            wz = get(self.bounds[4], self.bounds[5], j_grid)
            wx = np.zeros_like(wy)
            
            points_3d = np.stack([wx, wy, wz], axis=-1)
            points_2d = view.real_to_plane_batch(points_3d.reshape(-1, 3))
            points_2d = points_2d.reshape(res, res, 2)
            
            mask = view.points_inside_polygon_batch(points_2d)
            self.voxel_space &= mask[np.newaxis, :, :]


    def generate_surface(self) -> None:
        """ Gathers the real coordinates of the model voxels """
        # calculate cube size
        res = self.resolution
        size_x = (self.bounds[1] - self.bounds[0]) / self.resolution
        size_y = (self.bounds[3] - self.bounds[2]) / self.resolution
        size_z = (self.bounds[5] - self.bounds[4]) / self.resolution
        self.cube_size = (size_x, size_y, size_z)
        
        # get active voxels indices
        active_idx = np.argwhere(self.voxel_space)
        if not len(active_idx):
            self.cubes = []
            return

        # vectorized coordinate calculation
        fx = lambda a, b, i: a + i * (b - a) / res
        cx = fx(self.bounds[0], self.bounds[1], active_idx[:, 0])
        cy = fx(self.bounds[2], self.bounds[3], active_idx[:, 1])
        cz = fx(self.bounds[4], self.bounds[5], active_idx[:, 2])
        self.cubes = list(zip(cx, cy, cz))
        return self


    def draw_model(self) -> None:
        size = self.cube_size
        for (cx, cy, cz) in self.cubes:
            center = rl.Vector3(cx, cz, cy)
            rl.draw_cube(center, size[0], size[1], size[2], rl.WHITE)
            rl.draw_cube_wires(center, size[0], size[1], size[2], rl.BLACK)


    def additional_info(self) -> None:
        info = (f"[+] Model additional information:\n"
            f"Model bounds: {self.bounds}\n"
            f"Number of voxels: {self.resolution ** 3}\n"
            f"Number of active voxels: {len(self.cubes)}")
        print(info)