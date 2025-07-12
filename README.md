
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

```
proyecto/
├── main.py
├── core/
│   ├── base_model.py
│   ├── model_render.py
│   ├── simple/
│   │   ├── model.py
│   │   └── view.py
│   └── complex/
│       ├── model.py
│       └── view.py
```

### Componentes principales

- `main.py`: Punto de entrada del programa. Gestiona los argumentos de línea de comandos y lanza el proceso de reconstrucción.
- `core/base_model.py`: Define la clase base para los modelos de reconstrucción, con la lógica común para cargar vistas y coordinar el flujo general.
- `core/model_render.py`: Sistema de renderizado 3D para visualizar el modelo reconstruido de forma interactiva.

### Algoritmos

#### Algoritmo Simple (Vóxeles)
- `core/simple/model.py`: Reconstrucción en un espacio de vóxeles, eliminando los que no encajan con las vistas.
- `core/simple/view.py`: Procesa las vistas para verificar la coherencia de los vóxeles con los contornos.

#### Algoritmo Complejo (Estado del Arte)
- `core/complex/model.py`: Implementa la lógica del algoritmo de Gálvez Lamolda con intersección de planos y refinamiento.
- `core/complex/view.py`: Rasteriza las vistas y genera segmentos para las intersecciones.
