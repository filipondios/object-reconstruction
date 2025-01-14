import pyray as rl
import numpy as np

# Converts a (x,z) point inside a image (that is a projection plane)
# to a 3D point in space. vx and vz are direction vectors of the image, 
# paralell to the plane and 'o' is the 3D coordinate of the center of
# the image in space.

def transform2Dto3D(o, x, z, vx, vz):
    # origin + x * vx + z * vz
    return rl.Vector3(
        (x * vx.x) + (z * vz.x) + o.x,
        (x * vx.y) + (z * vz.y) + o.y, 
        (x * vx.z) + (z * vz.z) + o.z
    )


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
        self.image = image

        self.vertices = []
        (rows, cols) = self.image.shape

        for row in range(1, rows - 1, 1):
            z_rel = row - (rows >> 1)

            for col in range(1, cols - 1, 1):
                
                if image[row][col] != 0:
                    continue
                x_rel = col - (cols >> 1)

                # Given a 3x3 pixels neighbourhood centered at the pixel at (row,column)=(i,j),
                # add the values at the center row and column to know how many black and white
                # pixels are there in those pixels.
                
                rowv = np.int16(image[row][col]) + np.int16(image[row][col - 1]) + np.int16(image[row][col + 1])
                colv = np.int16(image[row][col]) + np.int16(image[row - 1][col]) + np.int16(image[row + 1][col])

                if not ((rowv == 0 and colv == 510) or (colv == 0 and rowv == 510)):
                    # Corner detected (not a horizontal or vertical line).
                    self.vertices.insert(0, transform2Dto3D(self.position, x_rel, z_rel, vx, vz))