import pyray as rl

# Converts a (x,z) point inside a image (that is a projection plane)
# to a 3D point in space. vx and vz are direction vectors of the image,
# paralell to the plane and 'o' is the 3D coordinate of the center of
# the image in space.

def transform_2D_3D(o, x, z, vx, vz):
    # origin + x * vx + z * vz
    return rl.Vector3(
        (x * vx.x) + (z * vz.x) + o.x,
        (x * vx.y) + (z * vz.y) + o.y, 
        (x * vx.z) + (z * vz.z) + o.z
    )


# Calculates the D parameter for a plane Ax + By + Cz + D = 0
# that contains a point (x,y,z) and is perpendicular to a vector (vx,vy,vz).
# The parameters A,B and C are already known because they are the same
# as the perpendicular vector coordinates (A=vx, B=vy, C=vz).

def calculate_plane_d(x,y,z, vx,vy,vz):
    return -(vx*x + vy*y + vz*z)


# Calculates the intersection point between a plane Ax + By + Cz + D = 0
# and a line that contains a point (x,y,z) and has the direction vector
# (vx, vy, vz) = (A,B,C). As you can see, the plane and the line will be 
# perpendicular to each other.

def intersect_plane_line(A,B,C,D, x,y,z):
    t = -(A*x + B*y + C*z + D)/(A*(A) + B*(B) + C*(C))
    return rl.Vector3(x + t * (A), y + t * (B),  z + t * (C))