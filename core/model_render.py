import pyray as rl
import math
import json
import os
from core.base_model import BaseModel


class ModelRender:

    camera_speed: float
    camera_margin: float
    camera_fovy: float
    initial_view_angles: tuple[float, float, float]

    base_width: int
    base_height: int
    aspect_ratio: tuple[int, int]
    text_fontsize: int
    box: tuple[int, int, int, int]

    camera: rl.Camera3D
    model:  BaseModel
    horizontal_rotation_axis: rl.Vector3
    vertical_rotation_axis:   rl.Vector3


    def __init__(self, model: BaseModel):
        """ Initializes the 3D camera and space using the default 
            parameters from the config file 'config/render.json'. """

        with open(os.path.join('config', 'render.json'), 'r') as file:
            data = json.load(file)
            ui_base = data['ui_base']
            camera = data['camera']

            self.camera_speed = camera['speed']
            self.camera_margin = camera['margin']
            self.camera_fovy = camera['fovy']
            angles = camera['initial_angles']
            self.initial_view_angles = (angles['x'], angles['y'], angles['z'])

            self.base_width = ui_base['canvas_width']
            self.base_height = ui_base['canvas_height']           
            aspect_ratio = ui_base['aspect_ratio']
            self.aspect_ratio = (aspect_ratio['width'], aspect_ratio['height'])
            self.text_fontsize = ui_base['font_size']
            self.box = tuple(ui_base['textbox_rectangle'])
        self.model = model

        # Initialize the render camera based on the model's bounding box
        position = self.calculate_camera_position()
        self.camera = rl.Camera3D(position, rl.Vector3(0,0,0), rl.Vector3(0,1,0),
            self.camera_fovy, rl.CameraProjection.CAMERA_PERSPECTIVE)

        # Create two vectors to rotate the camera around the model
        self.horizontal_rotation_axis = rl.vector3_normalize(rl.Vector3(position.z, 0., -position.x))
        self.vertical_rotation_axis = self.camera.up


    def calculate_camera_position(self) -> rl.Vector3:
        """
        Calculates a camera position such that the entire model (bounded by
        its bounding box) is guaranteed to be visible in the view frustum,
        regardless of its size.
        """

        (min_x, max_x, min_y, max_y, min_z, max_z) = self.model.bounds

        # Calculate model's bounding box center
        center = rl.Vector3(
            (min_x + max_x) / 2.0,
            (min_y + max_y) / 2.0,
            (min_z + max_z) / 2.0)

        # Bounding sphere radius
        rx = (max_x - min_x) / 2.0
        ry = (max_y - min_y) / 2.0
        rz = (max_z - min_z) / 2.0
        radius = math.sqrt(rx * rx + ry * ry + rz * rz)

        # Calculate screen aspect ratio and field of view constraints
        aspect_ratio = self.aspect_ratio[0] / self.aspect_ratio[1]
        fov_y_radians = math.radians(self.camera_fovy)
        fov_x_radians = 2.0 * math.atan(math.tan(fov_y_radians / 2.0) * aspect_ratio)

        # Determine minimum distance to fit entire model in view
        limiting_fov = min(fov_y_radians, fov_x_radians)
        distance = radius / math.sin(limiting_fov / 2.0)
        distance *= (1 + self.camera_margin)

        # Calculate the camera angle offset over the 'center' vector
        angle_x_rad = math.radians(self.initial_view_angles[0])
        angle_y_rad = math.radians(self.initial_view_angles[1])
        angle_z_rad = math.radians(self.initial_view_angles[2])

        offset_x = distance * math.sin(angle_x_rad)
        offset_y = distance * math.sin(angle_y_rad)
        offset_z = distance * math.sin(angle_z_rad)
        return rl.vector3_add(center, rl.Vector3(offset_x, offset_y, offset_z))


    def rotate_horizontally(self, clockwise: bool):
        """ Rotates the camera arround the vertical axis """
        if clockwise: speed = self.camera_speed
        else: speed = -self.camera_speed

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
        if clockwise: speed = self.camera_speed
        else: speed = -self.camera_speed

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
        #if not rotated: self.rotate_horizontally(True)


    def initialize(self):
        """ Initializes the Raylib 3D context """
        rl.set_config_flags(rl.ConfigFlags.FLAG_FULLSCREEN_MODE)
        rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
        rl.init_window(0, 0, self.model.path)
        rl.set_target_fps(60)

        monitor = rl.get_current_monitor()
        h = rl.get_monitor_height(monitor)
        w = rl.get_monitor_width(monitor)
        rl.set_window_size(w, h)

        self.width_scale  = int(w/self.base_width)
        self.height_scale = int(h/self.base_height)
        self.box = (
            self.box[0] * self.width_scale,
            self.box[1] * self.height_scale,
            self.box[2] * self.width_scale,
            self.box[3] * self.height_scale)
        self.text_fontsize = self.text_fontsize * self.width_scale

    
    def zoom(self):
        zoom = rl.get_mouse_wheel_move()
        if zoom == 0:
            return
        
        if zoom < 0:
            # zoom out, away from the object
            norm = rl.vector3_normalize(self.camera.position)
            movement = rl.vector3_scale(norm, 2.)
            self.camera.position = rl.vector3_add(self.camera.position, movement)
        elif zoom > 0:
            # zoom in, towards the object
            norm = rl.vector3_normalize(self.camera.position)
            movement = rl.vector3_scale(norm, 2.)
            self.camera.position = rl.vector3_subtract(self.camera.position, movement)


    def render_loop(self):
        """ Draws the reconstructed model """
        while not rl.window_should_close():
            self.move_camera()
            self.zoom()

            rl.begin_drawing()
            rl.clear_background(rl.BLACK)            
            rl.begin_mode_3d(self.camera)
            self.model.draw_model()
            rl.end_mode_3d()

            # Dibujar un rectangulo donde mostrar informacion
            rl.draw_rectangle_rec(self.box, rl.fade(rl.SKYBLUE, 0.5))
            rl.draw_rectangle_lines_ex(self.box, 2 * self.height_scale, rl.BLUE)

            rl.draw_text(
                'Object camera controls:',
                self.box[0] * 2,
                self.box[1] * 2,
                self.text_fontsize,
                rl.BLACK)
            rl.draw_text(
                '[Esc] to close the program',
                self.box[0] * 2,
                int(self.box[1] * 5),
                self.text_fontsize,
                rl.fade(rl.BLACK, 0.7))
            rl.draw_text(
                '[Mouse wheel] to zoom in-out',
                self.box[0] * 2,
                int(self.box[1] * 8),
                self.text_fontsize,
                rl.fade(rl.BLACK, 0.7))
            rl.draw_text(
                '[Right/Left/Up/Down] to rotate the object',
                self.box[0] * 2,
                int(self.box[1] * 11),
                self.text_fontsize,
                rl.fade(rl.BLACK, 0.7))
            rl.end_drawing()
        rl.close_window()
