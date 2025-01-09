import pyray as rl

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
    
        for z in range(rows):
            row = image[z]
            z_rel = z - (rows >> 1)

            for x in range(cols):
                x_rel = x - (cols >> 1)

                if row[x] == 255:
                    continue
                if x - 1 >= 0 and row[x - 1] == 255:
                    self.vertices.insert(0, transform2Dto3D(self.position, x_rel, z_rel, vx, vz))
                    continue
                if x + 1 <= cols and row[x + 1] == 255:
                    self.vertices.insert(0, transform2Dto3D(self.position, x_rel, z_rel, vx, vz))