# Object Reconstruction

Este repositorio contiene el código fuente de mi Trabajo de Fin de Grado (TFG).

## Descripción

El objetivo de este proyecto es comparar dos enfoques diferentes para la reconstrucción de objetos tridimensionales a partir de sus vistas ortogonales (frontal, lateral y superior), bajo un conjunto de restricciones concretas:

- Los objetos **no contienen rampas**: todas las caras son paralelas a al menos uno de los ejes del espacio (x, y, z).
- Los objetos **no tienen superficies circulares**: todas las caras son planas.
- Los objetos **no tienen huecos interiores**.

## Algoritmos Comparados

### 1. Algoritmo del Estado del Arte

Se ha seleccionado como algoritmo representativo del estado del arte a la tesis doctoral de Gálvez Lamolda:
> Gálvez Lamolda, J. M. (1990). *Reconstrucción de objetos a partir de vistas bidimensionales y su reconocimiento mediante momentos 3D: Desarrollos técnicos y aplicaciones*. AccedaCRIS ULPGC.  
> [Acceso al documento](https://accedacris.ulpgc.es/handle/10553/21247)

En dicho trabajo se presenta un algoritmo que teoricamente puede trabajar con todo tipo de objetos (incluyendo aquellos que no cumplen las restricciones descritas en la seccion anterior).

### 2. Algoritmo Propuesto (Vóxeles)

Por otro lado, el algoritmo que se ha implementado para ser comparado con el seleccionado del estado del arte está basado en [vóxeles](https://en.wikipedia.org/wiki/Voxel), los cuales ofrecen una solución perfecta para este problema ya que los objetos a tratar son perfectamente 'divisibles' visualmente en cubos.
