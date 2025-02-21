import numpy as np
import utils

class View:

    """
    A view is the combination of an image representing the projection of a 
    an object in an orthogonal space at a position and the 3 orientation 
    axis of that plane in space.

    The center of the image is stored at 'position'.
    The direction vectors are vx, vy and vz. 
    
    You can find more information about the plane position and direction
    vectors by looking at the Model class.
    """

    def __init__(self, image, position, vx, vy, vz):
        self.position = position
        self.vx = vx
        self.vy = vy
        self.vz = vz

        self.vertices = []
        (rows, cols) = image.shape

        for row in range(1, rows - 1, 1):
            z_rel = (rows >> 1) - row

            for col in range(1, cols - 1, 1):
                
                if image[row][col] != 0:
                    continue
                x_rel = col - (cols >> 1)

                # Given a 3x3 pixels neighbourhood centered at the pixel at (row,column)=(i,j),
                # add the values at the center row and column to know how many black and white
                # pixels are there in those pixels.
                
                rowv = image[row][col - 1] & image[row][col + 1]
                colv = image[row - 1][col] & image[row + 1][col]

                if (rowv == 0) and (colv == 0):
                    # Corner detected (not a horizontal or vertical line).
                    self.vertices.insert(0, utils.transform_2D_3D(self.position, x_rel, z_rel, vx, vz))
