#import pyray as rl
from model import Model

"""
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

ud_axis = rl.vector3_normalize(rl.Vector3(camera.position.z, 0, -camera.position.x))
lr_axis = rl.Vector3(0,1,0)
"""


# Cargar modelo
model = Model('cube')

"""

while(not rl.window_should_close()):
    if(rl.is_key_down(rl.KeyboardKey.KEY_RIGHT)):
        # Rotate the camera counter-clockwise horizontally. The up/down axis must be
        # also rotated to preserve being perpendicular to the camera direction vector.
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
    rl.end_mode_3d()
    rl.end_drawing()
rl.close_window()
"""