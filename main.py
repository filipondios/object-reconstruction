import pyray as rl
from model import Model

rl.init_window(1000, 700, "3D Reconstruction")
rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
rl.set_target_fps(60)

# Initialize the 3D Camera
camera = rl.Camera3D()
camera.projection = rl.CameraProjection.CAMERA_ORTHOGRAPHIC
camera.position   = rl.Vector3(40,40,40)
camera.target     = rl.Vector3(0,0,0)
camera.up         = rl.Vector3(0,1,0)
camera.fovy       = 90

model = Model('cube')
#model.reconstruct()
 

""" 
Camera rotation axis. The center of the rotation is the origin (0,0,0).

- 'ud_axis' stands for up/down axis, meaning the axis for a rotation inside a
   perpendicular plane to the XZ plane. It is calculated by taking the direction
   vector from the origin to the camera position, then calculating its projection
   to the XZ plane and then taking the perpendicular vector to the later.

- 'lr_axis' stands for left/right axis, meaning a rotation along the Y axis.
  It can also be thougt as a rotation over the origin inside a paralell plane
  to the XZ plane.
"""
 
ud_axis = rl.vector3_normalize(rl.Vector3(camera.position.z, 0, -camera.position.x))
lr_axis = rl.Vector3(0,1,0)

while(not rl.window_should_close()):
    if(rl.is_key_down(rl.KeyboardKey.KEY_RIGHT)):
        # Rotate the camera counter-clockwise horizontally. The up/down axis must be also rotated
        # to preserve being perpendicular to the camera direction vector.
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, lr_axis, 0.05)
        ud_axis = rl.vector3_rotate_by_axis_angle(ud_axis, lr_axis, 0.05)

    if(rl.is_key_down(rl.KeyboardKey.KEY_LEFT)):
        # Same as pressing KEY_RIGHT, but this time we rotate the camera clockwise.
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, lr_axis, -0.05)
        ud_axis = rl.vector3_rotate_by_axis_angle(ud_axis, lr_axis, -0.05)

    if(rl.is_key_down(rl.KeyboardKey.KEY_UP)):
        # Rotate the camera clockwise vertically
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, ud_axis, -0.05)

    if(rl.is_key_down(rl.KeyboardKey.KEY_DOWN)):
        # Rotate the camera counter-clockwise vertically
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, ud_axis, 0.05)

    rl.begin_drawing()
    rl.clear_background(rl.RAYWHITE)
    rl.begin_mode_3d(camera)

    # Draw the model
    for view in model.views:
        for vertex in view.vertices:
            # Use the raylib 'Y' axis as the 'Z' axis and vice versa.
            # We use 'Y' as depth, 'Z' as height and 'X' as width.
            pos = rl.Vector3(vertex.x, vertex.z, vertex.y)
            rl.draw_sphere(pos, 0.5, rl.BLACK)

    # Draw the 3D Axis [x,y,z]
    rl.draw_line_3d(rl.Vector3(0, 0, 0), rl.Vector3(1000, 0, 0), rl.RED)
    rl.draw_line_3d(rl.Vector3(0, 0, 0), rl.Vector3(0, 1000, 0), rl.BLUE)
    rl.draw_line_3d(rl.Vector3(0, 0, 0), rl.Vector3(0, 0, 1000), rl.GREEN)  

    # Draw the up/down vector as a line.
    v = rl.Vector3(ud_axis.x*100, ud_axis.y, ud_axis.z*100)
    rl.draw_line_3d(rl.vector3_negate(v), v, rl.GOLD)
    rl.end_mode_3d()
    rl.end_drawing()

rl.close_window()