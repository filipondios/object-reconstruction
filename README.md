
# Reconstrucción de Objetos

Este repositorio contiene el código fuente de mi Trabajo de Fin de Grado (TFG).

## Descripción

El objetivo de este proyecto es comparar dos enfoques diferentes para la reconstrucción de objetos tridimensionales a partir de sus vistas ortogonales (frontal, lateral, superior y sus opuestos), bajo un conjunto de restricciones concretas. Los objetos **no contienen** rampas, 
superficies circulares o huecos interiores.

## Algoritmos Comparados

### Algoritmo del Estado del Arte

Se ha seleccionado como algoritmo representativo del estado del arte a la tesis doctoral de Gálvez Lamolda:
> Gálvez Lamolda, J. M. (1990). *Reconstrucción de objetos a partir de vistas bidimensionales y su reconocimiento mediante momentos 3D: Desarrollos técnicos y aplicaciones*. AccedaCRIS ULPGC.  
> [Acceso al documento](https://accedacris.ulpgc.es/handle/10553/21247)

En dicho trabajo se presenta un algoritmo que teoricamente puede trabajar con todo tipo de objetos (incluyendo aquellos que no cumplen las restricciones descritas en la seccion anterior).

### Algoritmo Propuesto (Vóxeles)

Por otro lado, el algoritmo que se ha implementado para ser comparado con el seleccionado del estado del arte está basado en [vóxeles](https://en.wikipedia.org/wiki/Voxel), los cuales ofrecen una solución perfecta para este problema ya que los objetos a tratar son perfectamente 'divisibles' visualmente en cubos.

## Ejecución del programa

El programa tiene como punto de entrada el archivo `main.py` que se encuentra en la raiz del proyecto. Asegurate de instalar antes de nada 
los [requerimientos](requirements.txt).

```bash
python main.py [-h] -p <path> -c <complexity> [-s <step>] [-r <resolution>] [-i]
```

| Parámetro            | Obligatorio        | Valor por defecto | Descripción |
|:--------------------:|:------------------:|:-----------------:|:------------|
| `-p`                 | si                 | ninguno           | Ruta al modelo a reconstruir. |
| `-c`                 | si                 | ninguno           | Complejidad del algoritmo a usar para realizar la reconstrucción. Existen dos posiblilidades por defecto: `simple` o `complex`.  |
| `-s`                 | no                 | 1.0               | Separación entre segmentos de rasterización para el algoritmo `complex`. Cuanto menor separación, mayor precisión tendrá el modelo reconstruido. | 
| `-r`                 | no                 | 8                 | Resolución del espacio de vóxeles para el algoritmo `simple`. Cuanto mayor sea la resolución del espacio del vóxeles, mayor precisión tendra el modelo reconstruido. |
| `-i`                 | no                 | ninguno           | Mustra mas información sobre el modelo reconstruido al final del proceso de reconstrucción. |

<!-- Demo video, just trying some models from the examples -->
[![Demo video]](https://github.com/user-attachments/assets/d36af441-2e58-4a1c-be3e-91232300ddf8)

## Estructura del Proyecto

El proyecto tiene como punto de entrada el archivo `main.py`. Este se encarga de parsear los argumentos del programa e iniciar el proceso de 
reconstrucción. La reconstruccion de objetos se puede realizar mediante alguno de los algoritmos almacenados en `core/complex` o `core/simple`.

Ambos algoritmos hacen uso de las clases abstractas `BaseModel` y `BaseView`, pertenecientes a los archivos `core/base_model.py` y 
`core/base_view.py` para describir los objetos reconstruidos y sus vistas. Una vez reconstruido el objeto, se renderiza mediante
la clase `ModelRender` almacenada en `core/model_render.py`.


## Crear nuevos algoritmos de reconstrucción
### La clase BaseModel

Tal y como se ha explicado en el punto anterior, todos los algoritmos de este proyecto hacen uso de las clases `BaseModel` y `BaseView`. 
La clase `BaseModel` contiene metodos abstractos que definen cada una de las etapas de reconstruccion y que han de ser sobreescritos
por los algoritmos de reconstruccion, ademas de una funcion que dibuja el objeto reconstruido en un espacio 3D y otra que se encarga
de mostrar informacion adicional tras la reconstruccion.

```python
class BaseModel:

  def __init__(self, path: str, print_info: bool, viewClass: BaseView)
    # Inicializacion de otras propiedades...
    self.initial_reconstruction()
    self.refine_model()
    self.generate_surface()
    if self.print_info: self.additional_info()

  @abstractmethod
  def initial_reconstruction(self):
    warnings.warn('TODO')

  @abstractmethod
  def refine_model(self):
    warnings.warn('TODO')

  @abstractmethod
  def generate_surface(self):
    warnings.warn('TODO')

  @abstractmethod
  def draw_model(self):
    warnings.warn('TODO')

  @abstractmethod
  def additional_info(self):
    warnings.warn('TODO')
```

Tal y como se puede ver, en el constructor de la clase `BaseModel` se llaman a las tres funciones de reconstruccion de manera
secuencial y opcionalmente se muestra informacion adicional. Por otra parte, el metodo `draw_model` es usado en la clase 
`ModelRender` para renderizar el modelo 3D usando la libreria [raylib](https://github.com/ryu577/pyray).

> [!TIP]
> La clase BaseModel tiene atributos adicionales que proporcionan mas informacion. Estos son: una lista de vistas del objeto
> y una tupla que guarda las dimensiones o bounding box que encierran al objeto real. Para mas informacion, echale un vistazo
> a la clase [BaseModel](core/base_model.py)

### La clase BaseView

La idea tras la clase `BaseView` es almacenar toda la informacion relativa a una vista del modelo. Esto incluye la posicion y 
orientacion de la camara a la hora de tomar una imagen del objeto a reconstruir, lo cual se traduce en tres vectores `Vx`, `Vy`,
`Vz` y un punto `O`. 









