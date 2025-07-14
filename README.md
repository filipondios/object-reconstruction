
# Reconstrucción de Objetos

Este repositorio contiene el código fuente de mi Trabajo de Fin de Grado (TFG).

## Descripción

El objetivo de este proyecto es comparar dos enfoques diferentes para la reconstrucción de objetos tridimensionales a partir de sus vistas ortogonales (frontal, lateral, superior y sus opuestos), bajo un conjunto de restricciones concretas. Los objetos no contienen rampas, superficies circulares o huecos interiores.

## Algoritmos Comparados

### Algoritmo del Estado del Arte

Se ha seleccionado como algoritmo representativo del estado del arte a la tesis doctoral de Gálvez Lamolda:
> Gálvez Lamolda, J. M. (1990). *Reconstrucción de objetos a partir de vistas bidimensionales y su reconocimiento mediante momentos 3D: Desarrollos técnicos y aplicaciones*. AccedaCRIS ULPGC.  
> [Acceso al documento](https://accedacris.ulpgc.es/handle/10553/21247)

En dicho trabajo se presenta un algoritmo que teóricamente puede trabajar con todo tipo de objetos (incluyendo aquellos que no cumplen las restricciones descritas en la sección anterior).

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
| `-i`                 | no                 | ninguno           | Muestra más información sobre el modelo reconstruido al final del proceso de reconstrucción. |

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

Tal y como se ha explicado en el punto anterior, todos los algoritmos de este proyecto hacen uso de las clases ``BaseModel`` y ``BaseView``. La clase ``BaseModel`` contiene métodos abstractos que definen cada una de las etapas de reconstrucción y que han de ser sobrescritos por los algoritmos de reconstrucción, además de una función que dibuja el objeto reconstruido en un espacio 3D y otra que se encarga de mostrar información adicional tras la reconstrucción.

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

Tal y como se puede ver, en el constructor de la clase BaseModel se llaman a las tres funciones de reconstrucción de manera secuencial y, opcionalmente, se muestra información adicional. Por otra parte, el método draw_model es usado en la clase ModelRender para renderizar el modelo 3D usando la librería raylib.

> [!TIP]
> La clase BaseModel tiene atributos adicionales que proporcionan mas información. Estos son: una lista de vistas del objeto
> y una tupla que guarda las dimensiones o bounding box que encierran al objeto real. Para mas información, échale un vistazo
> a la clase [BaseModel](core/base_model.py)

### La clase BaseView

La idea tras la clase `BaseView` es almacenar toda la información relativa a una vista del modelo. Esto incluye la posición y 
orientación de la cámara a la hora de tomar una imagen del objeto a reconstruir, lo cual se traduce en tres vectores `Vx`, `Vy`,
`Vz` y un punto `O`, tal y como se puede observar en la siguiente imagen:

<div align='center'>
<img width="500" alt="imagen" src="https://github.com/user-attachments/assets/25266148-5bb3-4982-a6d1-bd185c790d0d" />
</div>

Además de la información acerca de la cámara, se guarda la linea poligonal (lista de puntos) 2D que define el contorno de la
proyección del objeto, es decir, la imagen que define la vista. Si bien se obtiene la linea poligonal del contorno de la vista,
no se obtienen polígonos interiores que pueden definir huecos trasversales.

La clase `BaseView` contiene además un metodo que permite proyectar puntos 3D al plano de la vista y pasarlos a puntos 2D relativos
al origen `O` de la vista, además de otro metodo que permite traducir coordenadas 2D relativas al origen de la vista a coordenadas 3D.

```python
class BaseView:

  def __init__(self, path: Path):
    # Inicializa Vx, Vy, Vz, O

  def plane_to_real(self, point: tuple[float, float]):
    # Convierte un punto 2D a 3D

  def real_to_plane(self, point: tuple[float, float, float]):
    # Convierte un punto 2D a 3D
```

Estos metodos son bastante útiles durante el proceso de reconstrucción ya que son usados en clases que heredan de `BaseModel` con
mucha frecuencia. A diferencia de `BaseModel`, `BaseView` ya contiene casi toda la información posible, por lo 
que es normal que nuevos algoritmos no hereden de `BaseView` sino que hagan uso directamente de la clase.

## Crear nuevos objetos

En el directorio ``examples/`` se encuentran algunos objetos junto con sus vistas correspondientes. Un modelo está compuesto por una
serie de subdirectorios, cada uno describiendo una vista. Cada vista ha de estar compuesta por un archivo `camera.json` que defina
la orientacion de la camara y su posición, ademas de la proyeccion ortogonal del objeto para dicha configuracion de la camara en 
el archivo `plane.bmp`. 

El contendio del archivo `camera.json` no es más que cada uno de los atributos para un objeto de la clase `BaseView`. Por ejemplo,
un archivo para describir la posición y orientación de la cámara puede tener el siguiente contenido:

```json
{
  "name": "elevation",
  "origin": [40,0,0],
  "vx": [0,-1,0],
  "vy": [-1,0,0],
  "vz": [0,0,1]
}
```

> [!NOTE]
> Se ha de mencionar que los vectores `Vx`, `Vy` y `Vz` deben de estar normalizados, ya que esto evitaria potenciales errores en los
> metodos de reconstrucción. Esto se produce debido a que al cargarlos en un objeto `BaseView` estos valores no se normalizan.

Por otro lado, las proyecciones de un objeto almacenadas en las imágenes `plane.bmp` deben tener el siguiente formato para poder
extraer de forma correcta la línea poligonal que describe el contorno de la proyección: La proyección debe tener un fondo blanco
`255`, los bordes de la figura proyectada serán negros `0` y la superficie de la figura de cualquier otro color RGB.






