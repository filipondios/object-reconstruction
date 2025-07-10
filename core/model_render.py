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
        """Initializes the 3D camera and space using config."""
        self.model = model       
        self.load_config(os.path.join('config', 'render.json'))
        self.setup_camera()

    
    def load_config(self, config_path: str):
        """Loads the render configuration from a JSON file."""
        with open(config_path, 'r') as file:
            data = json.load(file)
            ui_base = data['ui_base']
            camera = data['camera']

            # Parse camera config
            self.camera_speed = camera['speed']
            self.camera_margin = camera['margin']
            self.camera_fovy = camera['fovy']
            angles = camera['initial_angles']
            self.initial_view_angles = (angles['x'], angles['y'], angles['z'])
            self.auto_rotate = camera['auto_rotate']

            # Parse UI config
            self.base_width = ui_base['canvas_width']
            self.base_height = ui_base['canvas_height']           
            aspect_ratio = ui_base['aspect_ratio']
            self.aspect_ratio = (aspect_ratio['width'], aspect_ratio['height'])
            self.text_fontsize = ui_base['font_size']
            self.box = tuple(ui_base['textbox_rectangle'])


    def setup_camera(self):
        """Sets up the camera with the given position, target and up vector."""
        position = self.calculate_camera_position()
        self.camera = rl.Camera3D(position, rl.Vector3(0,0,0), rl.Vector3(0,1,0),
            self.camera_fovy, rl.CameraProjection.CAMERA_PERSPECTIVE)

        self.horizontal_rotation_axis = rl.vector3_normalize(rl.Vector3(position.z, 0., -position.x))
        self.vertical_rotation_axis = self.camera.up


    def calculate_camera_position(self) -> rl.Vector3:
        """Computes camera position to fit the model."""
        (min_x, max_x, min_y, max_y, min_z, max_z) = self.model.bounds

        center = rl.Vector3(
            (min_x + max_x) / 2.0,
            (min_y + max_y) / 2.0,
            (min_z + max_z) / 2.0)

        rx = (max_x - min_x) / 2.0
        ry = (max_y - min_y) / 2.0
        rz = (max_z - min_z) / 2.0
        radius = math.sqrt(rx * rx + ry * ry + rz * rz)

        aspect_ratio = self.aspect_ratio[0] / self.aspect_ratio[1]
        fov_y_radians = math.radians(self.camera_fovy)
        fov_x_radians = 2.0 * math.atan(math.tan(fov_y_radians / 2.0) * aspect_ratio)

        limiting_fov = min(fov_y_radians, fov_x_radians)
        distance = radius / math.sin(limiting_fov / 2.0)
        distance *= (1 + self.camera_margin)

        angle_x_rad = math.radians(self.initial_view_angles[0])
        angle_y_rad = math.radians(self.initial_view_angles[1])
        angle_z_rad = math.radians(self.initial_view_angles[2])

        offset_x = distance * math.sin(angle_x_rad)
        offset_y = distance * math.sin(angle_y_rad)
        offset_z = distance * math.sin(angle_z_rad)
        return rl.vector3_add(center, rl.Vector3(offset_x, offset_y, offset_z))


    def rotate_horizontally(self, clockwise: bool):
        """ Rotates the camera arround the vertical axis """
        speed = self.camera_speed if clockwise else -self.camera_speed
        self.camera.position = rl.vector3_rotate_by_axis_angle(
            self.camera.position, self.vertical_rotation_axis, speed)
        axis = rl.vector3_rotate_by_axis_angle(
            self.horizontal_rotation_axis, self.vertical_rotation_axis, speed)
        self.horizontal_rotation_axis = axis


    def rotate_vertically(self, clockwise: bool):
        """ Rotates the camera arround an axis in the ZX plane """
        speed = self.camera_speed if clockwise else -self.camera_speed
        self.camera.position = rl.vector3_rotate_by_axis_angle(
            self.camera.position, self.horizontal_rotation_axis, speed)


    def move_camera(self):
        """ Rotates the camera automatically if auto-rotate 
            is enabled, else checks for user input. """
        if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):
            self.auto_rotate = not self.auto_rotate

        if self.auto_rotate:
            self.rotate_horizontally(True)       
        elif rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):
            self.rotate_horizontally(False)
        elif rl.is_key_down(rl.KeyboardKey.KEY_LEFT):
            self.rotate_horizontally(True)
        if rl.is_key_down(rl.KeyboardKey.KEY_UP):
            self.rotate_vertically(True)
        elif rl.is_key_down(rl.KeyboardKey.KEY_DOWN):
            self.rotate_vertically(False)


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

        self.width_scale  = int(w / self.base_width)
        self.height_scale = int(h / self.base_height)
        self.box = (
            self.box[0] * self.width_scale,
            self.box[1] * self.height_scale,
            self.box[2] * self.width_scale,
            self.box[3] * self.height_scale)
        self.text_fontsize = self.text_fontsize * self.width_scale


    def zoom(self):
        """ Zooms the camera in or out based on mouse wheel movement.
            If there is no movement, the camera position remains unchanged. """
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


    def draw_help_box(self):
        """ Draws the help box with instructions for the user. """
        header_height = int(self.box[3] * 0.25)
        body_height = self.box[3] - header_height

        # Define rectangles
        header_rect = rl.Rectangle(self.box[0], self.box[1], self.box[2], header_height)
        body_rect = rl.Rectangle(self.box[0], self.box[1] + header_height, self.box[2], body_height)

        # Colors
        header_bg_color = rl.Color(204, 204, 204, 255)
        header_text_color = rl.Color(0, 0, 0, 255)
        body_bg_color = rl.Color(240, 240, 240, 136)
        body_text_color = rl.Color(51, 51, 51, 255)
        key_text_color = rl.Color(30, 30, 30, 255)
        border_color = rl.Color(170, 170, 170, 255)

        # Draw header
        rl.draw_rectangle_rec(header_rect, header_bg_color)
        rl.draw_text(
            'Object camera controls:',
            int(header_rect.x + 10),
            int(header_rect.y + header_height // 4),
            self.text_fontsize,
            header_text_color
        )

        rl.draw_rectangle_rec(body_rect, body_bg_color)
        rl.draw_rectangle_lines_ex(self.box, 2 * self.height_scale, border_color)

        # Add a top padding
        top_padding = 15 * self.height_scale
        side_padding = 10 * self.width_scale
        body_fontsize = max(1, self.text_fontsize - 1)
        line_spacing = int(body_fontsize * 1.5)

        body_lines = [
            ("[Esc]", "to close the program"),
            ("[Mouse wheel]", "to zoom in-out"),
            ("[Right | Left | Up | Down]", "to rotate the object"),
            ("[Space]", "to toggle auto-rotate"),
        ]

        for i, (key_part, description_part) in enumerate(body_lines):
            cursor_x = int(body_rect.x + side_padding)
            cursor_y = int(body_rect.y + top_padding + i * line_spacing)
            
            rl.draw_text(key_part, cursor_x, cursor_y, body_fontsize, key_text_color)
            cursor_x += rl.measure_text(key_part + ' ', body_fontsize)
            rl.draw_text(description_part, cursor_x, cursor_y, body_fontsize, body_text_color)


    def render_loop(self):
        """ Draws the reconstructed model """
        while not rl.window_should_close():
            self.move_camera()
            self.zoom()
            rl.begin_drawing()

            rl.clear_background(rl.Color(10,10,10,255))            
            rl.begin_mode_3d(self.camera)
            self.model.draw_model()
            rl.end_mode_3d()

            self.draw_help_box()
            rl.end_drawing()
        rl.close_window()
