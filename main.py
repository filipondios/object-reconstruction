import pyray as rl
from model import Model

# Images are indexed using a 2 color palette (black and white).
# The images precission is 8-bit.
model = Model('cube')



# Begin the renderization of the obtained object.
rl.init_window(1000, 1000, "3D Reconstruction")
rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
rl.set_target_fps(60)

camera = rl.Camera3D()
camera.projection = rl.CameraProjection.CAMERA_ORTHOGRAPHIC
camera.position = rl.Vector3(40, 40, 40)
camera.target = rl.Vector3(10,10,10)
camera.up = rl.Vector3(0,1,0)
camera.fovy = 89


while(not rl.window_should_close()):
    if(rl.is_key_down(rl.KeyboardKey.KEY_DOWN)):
        camera.position.y -= 10
    if(rl.is_key_down(rl.KeyboardKey.KEY_UP)):
        camera.position.y += 10
    if(rl.is_key_down(rl.KeyboardKey.KEY_LEFT)):
        camera.position.x -= 10
    if(rl.is_key_down(rl.KeyboardKey.KEY_RIGHT)):
        camera.position.x += 10

    rl.begin_drawing()
    rl.clear_background(rl.WHITE)
    rl.begin_mode_3d(camera)
    rl.draw_cube_wires(rl.Vector3(10,10,10), 20, 20, 20, rl.BLACK)

    # Draw the 3D Axis [x,y,z]
    rl.draw_line_3d(rl.Vector3(0, 0, 0), rl.Vector3(1000, 0, 0), rl.RED)
    rl.draw_line_3d(rl.Vector3(0, 0, 0), rl.Vector3(0, 1000, 0), rl.BLUE)
    rl.draw_line_3d(rl.Vector3(0, 0, 0), rl.Vector3(0, 0, 1000), rl.GREEN)

    

    rl.end_mode_3d()
    rl.end_drawing()

rl.close_window()