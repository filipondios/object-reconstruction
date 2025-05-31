from core.base_view import BaseView
import numpy as np
import cv2


class View(BaseView):

    vertices: list[(int, int)]
    projection: np.ndarray 

    def __init__(self, path):
        super().__init__(path)

        # Get the visible vertices from the view.
        projection = path.joinpath('plane.bmp')
        img = cv2.imread(projection, cv2.IMREAD_GRAYSCALE)
        self.vertices = self.extract_vertices(img)
        self.projection = img


    def extract_vertices(self, img: np.ndarray):
        (rows, cols) = img.shape
        x0 = cols >> 1
        z0 = rows >> 1
        vertices = []

        for zi in range(1, rows - 1, 1):
            z_rel = z0 - zi

            for xi in range(1, cols - 1, 1):
                if img[zi][xi] != 0x00:
                    # Vertices are black
                    continue

                rowv = img[zi][xi - 1] & img[zi][xi + 1]
                colv = img[zi - 1][xi] & img[zi + 1][xi]

                if (rowv == 0x00) and (colv == 0x00):
                    vertices.append((xi - x0, z_rel))
        return vertices
    

    def plane_to_image(self, point):
        (rows, cols) = self.projection.shape
        x = point[0] + (cols >> 1)
        z = -(point[1] - (rows >> 1))
        return (x, z)
