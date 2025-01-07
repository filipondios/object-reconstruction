from view import View
import pyray as rl
import cv2
import os

class Model:

    """
    Un modelo consta de un directorio nombrado con el formato 'model_nombre'.
    El directorio estará compuesto de varios subdirectiorios, cada cual almacenando
    una imagen del plano imagen de una vista y un archivo que informe en que punto
    del espacio se tomó la vista.
    
    El archivo del plano imagen se llamará 'plane.bmp' y el archivo donde se detalla
    la posicion de la camara para dicha vista en 'camera'.
    """

    model_prefix = 'model_'
    camera_file = 'camera'
    image_view_file  = 'plane.bmp' 

    def __init__(self, model_name: str):
        # Intentar obtener las vistas del modelo
        self.model_name = self.model_prefix + model_name
        self.views = []

        for view_dir in os.listdir(self.model_name):
            view_path = os.path.join(self.model_name, view_dir)

            if os.path.isdir(view_path) and view_dir.startswith('view'):
                # Intentar obtener la imagen de la vista
                img = cv2.imread(os.path.join(view_path, self.image_view_file), cv2.IMREAD_GRAYSCALE)
                
                # Intentar obtener la posicion de la camara
                with open(os.path.join(view_path, self.camera_file)) as file:
                    content = file.read()
                content = content.split('\n')
                pos = rl.Vector3(int(content[0]), int(content[1]), int(content[2]))

                # Guardar los datos de la vista actual
                self.views.append(View(pos, img))