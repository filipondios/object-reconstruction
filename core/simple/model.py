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
        self.reconstruct_model()
        self.generate_edges()


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


    def reconstruct_model(self):
        """ Reconstructs the model directly """
        self.voxel_space = np.ones((self.resolution,)*3, dtype=bool)
        self.bounds = self.calculate_world_bounds()

        for view in self.views:
            # Merge each view voxel space with the model's
            print(f'[+] Using {view.name} to reconstruct.')
            self.voxel_space &= self.project_view_to_voxels(view)


    def project_view_to_voxels(self, view: View):
        voxels = np.zeros((self.resolution,) * 3, dtype=bool)
        get = lambda a, b, i: a + i * (b - a) / (self.resolution - 1)
        d = view.get_view_direction()

        for i in range(self.resolution):
            for j in range(self.resolution):
                if d == 'xy':
                    wx = get(self.bounds[0], self.bounds[1], i)
                    wy = get(self.bounds[2], self.bounds[3], j)
                    if view.is_point_inside_contour(view.real_to_plane([wx, wy, 0])):
                        voxels[i, j, :] = True
                elif d == 'xz':
                    wx = get(self.bounds[0], self.bounds[1], i)
                    wz = get(self.bounds[4], self.bounds[5], j)
                    if view.is_point_inside_contour(view.real_to_plane([wx, 0, wz])):
                        voxels[i, :, j] = True
                elif d == 'yz':
                    wy = get(self.bounds[2], self.bounds[3], i)
                    wz = get(self.bounds[4], self.bounds[5], j)
                    if view.is_point_inside_contour(view.real_to_plane([0, wy, wz])):
                        voxels[:, i, j] = True
        return voxels


    def generate_edges(self):
        faces = [
            (1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)
        ]
        edge_set = set()
        R = self.resolution

        for x in range(R):
            for y in range(R):
                for z in range(R):
                    if not self.voxel_space[x, y, z]: continue
                    for dx, dy, dz in faces:
                        nx, ny, nz = x + dx, y + dy, z + dz
                        if 0 <= nx < R and 0 <= ny < R and 0 <= nz < R and self.voxel_space[nx, ny, nz]:
                            continue
                        for i in range(4):
                            a, b = self.face_edge_corners(x, y, z, (dx, dy, dz), i)
                            edge = tuple(sorted((tuple(a), tuple(b))))
                            edge_set.add(edge)

        self.edges = [(self._voxel_to_world(a), self._voxel_to_world(b)) for a, b in edge_set]
        print(f'[+] Generated {len(self.edges)} surface edges')


    def face_edge_corners(self, x, y, z, normal, idx):
        offsets = {
            (1, 0, 0):  [[1,0,0],[1,1,0],[1,1,1],[1,0,1]],
            (-1, 0, 0): [[0,0,0],[0,0,1],[0,1,1],[0,1,0]],
            (0, 1, 0):  [[0,1,0],[0,1,1],[1,1,1],[1,1,0]],
            (0, -1, 0): [[0,0,0],[1,0,0],[1,0,1],[0,0,1]],
            (0, 0, 1):  [[0,0,1],[1,0,1],[1,1,1],[0,1,1]],
            (0, 0, -1): [[0,0,0],[0,1,0],[1,1,0],[1,0,0]]
        }
        corners = offsets[normal]
        return [[x+a, y+b, z+c] for a,b,c in [corners[idx], corners[(idx+1)%4]]]


    def _voxel_to_world(self, coord):
        x, y, z = coord
        fx = lambda a, b, i: a + i * (b - a) / self.resolution
        return [fx(self.bounds[0], self.bounds[1], x),
                fx(self.bounds[2], self.bounds[3], y),
                fx(self.bounds[4], self.bounds[5], z)]


    def drawModel(self):
        for a, b in self.edges:
            va = rl.Vector3(a[0], a[2], a[1])
            vb = rl.Vector3(b[0], b[2], b[1])
            rl.draw_line_3d(va, vb, rl.WHITE)