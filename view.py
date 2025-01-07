import pyray as rl
import cv2

class View:

    """
    Una vista es la combinacion de una imagen y que representa el plano imagen
    de una vista de un objeto en un espacio ortogonal y un vector posicion de 
    dicho plano para formar la vista. 
    """

    def __init__(self, position: rl.Vector3, image: cv2.Mat):
        self.position = position
        self.image = image
        self.vertices = []
        (rows, cols) = self.image.shape
    
        for i in range(rows):
            row = image[i]

            for j in range(cols):
                if row[j] == 255:
                    continue
                if j - 1 > 0 and row[j - 1] == 255:
                    self.vertices.append(rl.Vector2(i,j))
                    continue
                if j + 1 < cols and row[j + 1] == 255:
                    self.vertices.append(rl.Vector2(i,j))