import pyray as rl
from core.base_model import BaseModel


class ModelRender:

    camera: rl.Camera3D
    model: BaseModel
    horizontal_rotation_axis: rl.Vector3
    vertical_rotation_axis: rl.Vector3

    def __init__(self, model: BaseModel):
        """ Initializes the 3D camera and space """
        self.model = model
        self.origin = rl.Vector3(0,0,0)

        self.camera = rl.Camera3D(rl.Vector3(40,40,40), self.origin,
            rl.Vector3(0,1,0), 90., rl.CameraProjection.CAMERA_ORTHOGRAPHIC)
        self.horizontal_rotation_axis = rl.vector3_normalize(rl.Vector3(
            self.camera.position.z, 0., -self.camera.position.x))
        self.vertical_rotation_axis = rl.Vector3(0,1,0)

        self.rotation_speed = 0.02
        self.text_fontsize = 20
        self.text_x = 10
        self.text_y = 10
        self.base_width = 1366
        self.base_height = 768


    def rotate_horizontally(self, clockwise: bool):
        """ Rotates the camera arround the vertical axis """
        if clockwise: speed = self.rotation_speed
        else: speed = -self.rotation_speed

        self.camera.position = rl.vector3_rotate_by_axis_angle(
            self.camera.position, self.vertical_rotation_axis,
            speed)
        
        axis = rl.vector3_rotate_by_axis_angle(
            self.horizontal_rotation_axis, self.vertical_rotation_axis,
            speed)
        
        self.horizontal_rotation_axis.x = axis.x
        self.horizontal_rotation_axis.y = axis.y
        self.horizontal_rotation_axis.z = axis.z


    def rotate_vertically(self, clockwise: bool):
        """ Rotates the camera arround an axis in the ZX plane """
        if clockwise: speed = self.rotation_speed
        else: speed = -self.rotation_speed

        self.camera.position = rl.vector3_rotate_by_axis_angle(
            self.camera.position, self.horizontal_rotation_axis,
            speed)


    def move_camera(self):
        """ Rotates the camera automatically if the user is not
            pressing a rotation key (one of the arrow keys). """
        rotated = False

        if(rl.is_key_down(rl.KeyboardKey.KEY_RIGHT)):
            self.rotate_horizontally(False)
            rotated = True
        elif(rl.is_key_down(rl.KeyboardKey.KEY_LEFT)):
            self.rotate_horizontally(True)
            rotated = True
        if(rl.is_key_down(rl.KeyboardKey.KEY_UP)):
            self.rotate_vertically(True)
            rotated = True    
        elif(rl.is_key_down(rl.KeyboardKey.KEY_DOWN)):
            self.rotate_vertically(False)
            rotated = True
        if not rotated: self.rotate_horizontally(True)


    def initialize(self):
        """ Initializes the Raylib 3D context """
        rl.set_config_flags(rl.ConfigFlags.FLAG_FULLSCREEN_MODE)
        rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
        rl.init_window(0, 0, self.model.path)
        rl.set_target_fps(60)

        monitor = rl.get_current_monitor()
        height = rl.get_monitor_height(monitor)
        width = rl.get_monitor_width(monitor)
        rl.set_window_size(width, height)

        width_ratio = int(width/self.base_width)
        height_ratio = int(height/self.base_height)
        self.text_y = self.text_y * height_ratio
        self.text_x = self.text_x * width_ratio
        self.text_fontsize = self.text_fontsize * width_ratio 


    def render_loop(self):
        """ Draws the reconstructed model """
        while not rl.window_should_close():
            self.move_camera()
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)            
            rl.begin_mode_3d(self.camera)

            self.model.draw_model()
            
            rl.end_mode_3d()
            rl.draw_text(
                "Press [Esc] to close the program",
                self.text_x,
                self.text_y,
                self.text_fontsize,
                rl.WHITE
            )
            rl.end_drawing()
        rl.close_window()