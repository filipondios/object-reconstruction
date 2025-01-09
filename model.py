from view import View
import pyray as rl
import cv2
import os
import json

class Model:

    """
    A model is a directory named with the format 'model_name' that contains 
    sub-directories named 'view..'. Each subdirectory must contain a file
    'plane.bmp' (tha image projection plane) and a 'camera.json' file with
    details about the camera position and angle.
    
    The requirements for the files plane.bmp are:
        
        - It must be a greyscale image, with only two colors: black and white (0/255)

        - The pixel at the center of the image must be the intersection point of a 
          perpendicular line to the projection plane that also passes at the origin 
          of the space (0,0,0). The line is the camera vision line and the point is
          the camera position.

    The requirements for the files camera.json are:

        - It must contain a object 'position', with three fields 'x', 'y', 'z', and
          the objects 'vx', 'vy', 'vz' with the same fields as 'position'.
        
        - 'position' describes the coordinate in space of the camera/projection plane 
          (same as the point described in the 'plane.bmp' file requirements).
        
        - 'vx', 'vy', 'vz' describe the 3 direction vectors of the projection plane.
          All of them are perpendicular to each other. 'vy' must follow the direction
          of the camera (up to the origin). 'vx' must be pointing to the right of the
          projection and 'vz' up of the projection. All vectors are normalized.

    If you dont understand how the direction of the vectors 'vx' and 'vz' work, just 
    think that they are the axis of the 2D image/projection ('vx' being the horizontal
    axis and 'vz' the vertical axis, 'vx' is positive to the right and vz 'up').
    """


    model_prefix = 'model_'
    camera_file = 'camera.json'
    image_view_file  = 'plane.bmp' 

    def __init__(self, model_name: str):
        # Intentar obtener las vistas del modelo.
        self.model_name = self.model_prefix + model_name
        self.views = []

        for view_dir in os.listdir(self.model_name):
            view_path = os.path.join(self.model_name, view_dir)

            if os.path.isdir(view_path) and view_dir.startswith('view'):
                # Obtener la imagen de la vista.
                img = cv2.imread(os.path.join(view_path, self.image_view_file), cv2.IMREAD_GRAYSCALE)
                
                # Obtener detalles de la posicion de la camara.
                with open(os.path.join(view_path, self.camera_file)) as file:
                    json_data = json.load(file)

                    data = json_data['position']
                    pos = rl.Vector3(data['x'], data['y'], data['z'])
                    
                    data = json_data['vx']
                    vx = rl.Vector3(data['x'], data['y'], data['z'])
                    
                    data = json_data['vy']
                    vy = rl.Vector3(data['x'], data['y'], data['z'])
                    
                    data = json_data['vz']
                    vz = rl.Vector3(data['x'], data['y'], data['z'])
                    self.views.insert(0, View(img, pos, vx, vy, vz))


    def reconstruct(self):
        view0 = self.views[0]
        view1 = self.views[1]
        c = rl.vector3_cross_product(view0.vy, view1.vy)

        if c.x == 0 and c.y == 0 and c.z == 0:
          print("Both views have paralell vy vectors.")
          return
        
        intersections = []

        for c in view0.vertices:
            e = view0.vy

            for d in view1.vertices:
              f = view1.vy

              # Find intersection of two 3D lines
              # https://math.stackexchange.com/questions/270767/find-intersection-of-two-3d-lines
              
              g = rl.Vector3(c.x - d.x, c.y - d.y, c.z - d.z)
              fxg = rl.vector3_cross_product(f, g)
              fxe = rl.vector3_cross_product(f, e)
              h = rl.vector3_length(fxg)
              k = rl.vector3_length(fxe)

              if h == 0 or k == 0:
                # Lines do not intersect
                continue

              l = rl.vector3_scale(e, h/k)
              sign = rl.vector3_scale(rl.vector_3dot_product(fxg, fxe), 1/(h*k))

              if sign == 1:
                # f x g and f x e have the same direction
                intersections.insert(0, rl.vector3_add(c, l))
              else:
                  l.x = -l.x
                  l.y = -l.y
                  l.z = -l.z
                  intersections.insert(0, rl.vector3_add(c, l))