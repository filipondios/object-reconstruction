import pyray as rl
from model import Model


def draw_axes():
    color = rl.Color(0,0,0,50)
    rl.draw_line_3d(rl.Vector3(-500,0,0), rl.Vector3(500,0,0), color)
    rl.draw_line_3d(rl.Vector3(0,-500,0), rl.Vector3(0,500,0), color)
    rl.draw_line_3d(rl.Vector3(0,0,-500), rl.Vector3(0,0,500), color)


def move_camera(camera, ud_axis, lr_axis):
    # Rotate the camera counter-clockwise horizontally.
    if(rl.is_key_down(rl.KeyboardKey.KEY_RIGHT)):
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, lr_axis, 0.05)
        axis = rl.vector3_rotate_by_axis_angle(ud_axis, lr_axis, 0.05)
        ud_axis.x = axis.x
        ud_axis.y = axis.y
        ud_axis.z = axis.z

    # Rotate the camera clockwise horizontally.
    if(rl.is_key_down(rl.KeyboardKey.KEY_LEFT)):
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, lr_axis, -0.05)
        axis = rl.vector3_rotate_by_axis_angle(ud_axis, lr_axis, -0.05)
        ud_axis.x = axis.x
        ud_axis.y = axis.y
        ud_axis.z = axis.z

    # Rotate the camera clockwise vertically
    if(rl.is_key_down(rl.KeyboardKey.KEY_UP)):
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, ud_axis, -0.05)

    # Rotate the camera counter-clockwise vertically
    if(rl.is_key_down(rl.KeyboardKey.KEY_DOWN)):
        camera.position = rl.vector3_rotate_by_axis_angle(camera.position, ud_axis, 0.05)



if __name__ == "__main__":
    rl.init_window(1500, 1500, "3D Reconstruction")
    rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
    rl.set_target_fps(60)

    camera = rl.Camera3D()
    camera.projection = rl.CameraProjection.CAMERA_ORTHOGRAPHIC
    camera.position   = rl.Vector3(40,40,40)
    camera.target     = rl.Vector3(0,0,0)
    camera.up         = rl.Vector3(0,1,0)
    camera.fovy       = 90
    
    # Camera horizontal and vertical rotation axes.
    ud_axis = rl.vector3_normalize(rl.Vector3(camera.position.z, 0, -camera.position.x))
    lr_axis = rl.Vector3(0,1,0)

    # Load model
    model = Model('stairs')
    intersections = model.reconstruct()


    while(not rl.window_should_close()):
        move_camera(camera, ud_axis, lr_axis)
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

        for point in intersections:
            # Adapt coordinates to raylib's
            pos = rl.Vector3(point.x, point.z, point.y)
            rl.draw_sphere(pos, 0.5, rl.BLUE)
    
        draw_axes()
        rl.end_mode_3d()
        rl.end_drawing()
    rl.close_window()