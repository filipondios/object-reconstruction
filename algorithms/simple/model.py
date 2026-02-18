import numpy as np
import pyray as rl
from shapely import Point
from shapely.vectorized import contains
from core.base_model import BaseModel
from algorithms.simple.view import View
from utils.geo3d import Plane


class Model(BaseModel):

    resolution: int
    voxel_space: np.ndarray[np.bool_]
    cubes: list[tuple[float, float, float]]
    cube_size: tuple[float, float, float]

    def __init__(self, path: str, print_info: bool, resolution: int):
        self.resolution = resolution
        self.cubes = []
        super().__init__(path, print_info, View)


    def initial_reconstruction(self) -> None:
        """ Initializes the voxel space """
        self.voxel_space = np.ones((self.resolution,)*3, dtype=bool)


    def refine_model(self) -> None:
        """ Reconstructs the model directly """
        for view in self.views:
            # Merge each view voxel space with the model's
            print(f'[+] Using {view.name} to reconstruct.')
            self.project_view_to_voxels(view)


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
            points_2d = self.real_to_plane_batch(view, points_3d.reshape(-1, 3))
            points_2d = points_2d.reshape(res, res, 2)

            mask = self.points_inside_polygon_batch(view, points_2d)
            self.voxel_space &= mask[:, :, np.newaxis]
        
        elif d == Plane.XZ:
            # grid parallel to XZ plane
            i_grid, j_grid = np.meshgrid(indices, indices, indexing='ij')
            wx = get(self.bounds[0], self.bounds[1], i_grid)
            wz = get(self.bounds[4], self.bounds[5], j_grid)
            wy = np.zeros_like(wx)
            
            points_3d = np.stack([wx, wy, wz], axis=-1)
            points_2d = self.real_to_plane_batch(view, points_3d.reshape(-1, 3))
            points_2d = points_2d.reshape(res, res, 2)
            
            mask = self.points_inside_polygon_batch(view, points_2d)
            self.voxel_space &= mask[:, np.newaxis, :]
        
        elif d == Plane.YZ:
            # grid parallel to YZ plane
            i_grid, j_grid = np.meshgrid(indices, indices, indexing='ij')
            wy = get(self.bounds[2], self.bounds[3], i_grid)
            wz = get(self.bounds[4], self.bounds[5], j_grid)
            wx = np.zeros_like(wy)
            
            points_3d = np.stack([wx, wy, wz], axis=-1)
            points_2d = self.real_to_plane_batch(view, points_3d.reshape(-1, 3))
            points_2d = points_2d.reshape(res, res, 2)
            
            mask = self.points_inside_polygon_batch(view, points_2d)
            self.voxel_space &= mask[np.newaxis, :, :]

    
    def real_to_plane_batch(self, view: View, points: np.ndarray) -> np.ndarray:
        """ Vectorized version of view.real_to_plane (points = (n,3) -> (n,2)) """
        delta = points - view.origin
        solution = delta @ view.transform_inv.T
        return solution
    
    
    def points_inside_polygon_batch(self, view: View, points_2d: np.ndarray) -> np.ndarray:
        """ Vectorized polygon containement check """
        x = points_2d[:, :, 0].flatten()
        y = points_2d[:, :, 1].flatten()
        mask = contains(view.polygon, x, y)
        return mask.reshape(points_2d.shape[0], points_2d.shape[1])


    def generate_surface(self) -> None:
        """ Gathers the real coordinates of the model voxels """
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