
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
