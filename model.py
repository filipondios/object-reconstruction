import pyray as rl
import cv2

class Model:

    # Un modelo esta almacenado en una carpeta, con las
    # imagenes para la planta, alzado y perfil.
    # Tambien se compone de un archivo model.info que
    # contendra los puntos donde se tomaron dichas imagenes.

    model_prefix = 'model_'
    model_info = 'model.info'

    def __init__(self, model_name):
        # Obtener las imagenes del directorio del modelo
        self.model_name = self.model_prefix + model_name
        self.planta = cv2.imread(self.model_name + '/planta.bmp')
        self.alzado = cv2.imread(self.model_name + '/alzado.bmp')
        self.perfil = cv2.imread(self.model_name + '/perfil.bmp')

        # Obtener los puntos donde se han tomado las imagenes del
        # objeto 3D en las 3 diferentes perspectivas.
        with open(self.model_name + '/' + self.model_info, 'r') as file:
            content = file.read().split('\n')

            for line in content:
                sides = line.split('=')

                if sides[0] == 'PLANTA':
                    self.planta_pos = rl.Vector3(0, int(sides[1]), 0)
                elif sides[0] == 'ALZADO':
                    self.alzado_pos = rl.Vector3(int(sides[1]), 0, 0)
                elif sides[0] == 'PERFIL':
                    self.perfil_pos = rl.Vector3(0, 0, int(sides[1]))

    def extract_vertices(self):
        pass