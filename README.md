# Object Reconstruction

> [!NOTE]  
> This repository also contains a README in Spanish. If you prefer to read the documentation in Spanish, please refer to this [README](docs/README_ES.md). I also keep track of version changes at the [CHANGELOG](docs/CHANGELOG.md) file and there is more information about the project at the [wiki](https://github.com/filipondios/object-reconstruction/wiki).

This repository contains the source code for my Bachelor's Thesis project.

## Table of Contents

1. [Introduction](#introduction)  
2. [Compared Algorithms](#compared-algorithms)  
   2.1 [State-of-the-Art Algorithm](#state-of-the-art-algorithm)  
   2.2 [Proposed Algorithm (Voxels)](#proposed-algorithm-voxels)  
3. [Program Execution](#program-execution)  
4. [Benchmarks](#benchmarks)  
5. [Project Structure](#project-structure)  
6. [Possible Improvements to Current Algorithms](#possible-improvements-to-current-algorithms)  
7. [Creating New Reconstruction Algorithms](#creating-new-reconstruction-algorithms)  
   7.1 [The BaseModel Class](#the-basemodel-class)  
   7.2 [The BaseView Class](#the-baseview-class)  
   7.3 [Integrating the New Algorithm](#integrating-the-new-algorithm)  
8. [Creating New Objects](#creating-new-objects)  

## Introduction

The goal of this project is to compare two different approaches to the 
reconstruction of 3D objects from their orthogonal views (front, side, top, and
their opposites), under a specific set of constraints. The objects do not 
contain ramps, circular surfaces, or internal cavities.

## Compared Algorithms

### State-of-the-Art Algorithm

As a representative of the state-of-the-art, the following PhD thesis by Gálvez 
Lamolda has been selected:
> Gálvez Lamolda, J. M. (1990). *Reconstrucción de objetos a partir de vistas 
> bidimensionales y su reconocimiento mediante momentos 3D: Desarrollos técnicos
> y aplicaciones*. AccedaCRIS ULPGC. 
> [Access the document](https://accedacris.ulpgc.es/handle/10553/21247)

This work presents an algorithm that can theoretically work with all types of
objects, including those that do not comply with the constraints described in 
the previous section.

### Proposed Algorithm (Voxels)

On the other hand, the algorithm implemented for comparison with the state-of-
the-art solution is based on  [voxels](https://en.wikipedia.org/wiki/Voxel),
which offer a perfect solution for this problem since the objects are visually
'divisible' into cubes.

## Program Execution

The program's entry point is the `main.py` file located at the root of the
project. Make sure to first install the [requirements](requirements.txt).

```bash
python main.py [-h] -p <path> -c <complexity> [-s <step>] [-r <resolution>] [-i]
```

| Parameter | Required | Default Value | Description                                                                                                                  |
|:---------:|:--------:|:-------------:|:-----------------------------------------------------------------------------------------------------------------------------|
| `-p`      | yes      | none          | Path to the model to be reconstructed.                                                                                       |
| `-c`      | yes      | none          | Complexity of the algorithm used for reconstruction. Two default options are available: `simple` or `complex`.               |
| `-s`      | no       | 1.0           | Step size between raster segments for the `complex` algorithm. The smaller the step, the higher the reconstruction accuracy. |
| `-r`      | no       | 8             | Voxel space resolution for the `simple` algorithm. Higher resolution leads to more accurate reconstruction.                  |
| `-i`      | no       | none          | Displays additional information about the reconstructed model after the process ends.                                        |

<!-- Demo video, just trying some models from the examples -->
[![Demo video]](https://github.com/user-attachments/assets/d36af441-2e58-4a1c-be3e-91232300ddf8)

## Benchmarks

Below are the benchmark results for the two algorithms implemented in this 
project. First, the results obtained with José M. Gálvez's algorithm are shown,
followed by those of the voxel-based algorithm developed in this work.

The tables include two key columns:
- I.R (Initial Reconstruction): execution time (in seconds) for the model's 
initial reconstruction stage.
- M.R (Model Refinement): execution time (in seconds) for the subsequent 
refinement stage.

Each table shows the average values of five runs for each precision level using
the test model [someone](models/someone). Tests were conducted on a system 
with an AMD Ryzen 7 5800X CPU, 16 GB DDR4 RAM, and Windows OS.

Results for José M. Gálvez's algorithm implementation:

| Step (units) | I.R (ms) | M.R (ms) | Planes (units) | Polygons (units)  | Vertices (units) |
|--------------|----------|----------|----------------|-------------------|------------------|
| 8            | 4.2542   | 2.9248   | 17             | 19                | 115              |
| 7            | 3.9412   | 2.1471   | 18             | 17                | 105              |
| 6            | 4.1975   | 2.3298   | 20             | 20                | 128              |
| 5            | 7.3029   | 5.7738   | 30             | 45                | 253              |
| 4            | 7.0648   | 5.0973   | 32             | 41                | 245              |
| 3            | 8.1206   | 4.7164   | 39             | 46                | 286              |
| 2            | 11.7747  | 7.1158   | 60             | 69                | 425              |
| 1            | 21.1189  | 13.0215  | 118            | 133               | 821              |
| 0.5          | 36.9881  | 22.4789  | 228            | 243               | 1531             |

> [!NOTE]  
> Compared to v1.0.0, version v1.1.0 introduces significant performance optimizations. For the I.R function (using a 0.5 step), execution time was reduced from 16.313 seconds to 36.99 ms, representing a 99.77% time reduction (441.03x speedup). Similarly, the M.R function saw an improvement from 44.7234 seconds to 22.48 ms, achieving a 99.95% reduction and a massive 1,989.57x speedup. You can see the reasons for this improvement in the [CHANGELOG.md](docs/CHANGELOG.md) file.

Results for the simplified (voxel-based) algorithm implementation:

| Resolution (units) | I.R (ms)  | M.R (ms) | Total Voxels  | Active Voxels  | Active %  |
|--------------------|-----------|----------|---------------|----------------|-----------|
| 8                  | 0.0202    | 0.6887   | 512           | 52             | 10.1563   |
| 16                 | 0.0176    | 0.7191   | 4096          | 294            | 7.1777    |
| 24                 | 0.0203    | 0.8087   | 13824         | 1144           | 8.2755    |
| 32                 | 0.0189    | 0.9118   | 32768         | 2576           | 7.8613    |
| 48                 | 0.0646    | 1.2169   | 110592        | 8544           | 7.7257    |
| 64                 | 0.1205    | 1.5968   | 262144        | 22174          | 8.4587    |
| 96                 | 0.3580    | 3.5413   | 884736        | 70784          | 8.0006    |
| 128                | 0.4710    | 6.1159   | 2097152       | 167112         | 7.9685    |

> [!NOTE]  
> The optimization in v1.1.0 yielded even more dramatic results for the M.R function: execution time got a 99.98% reduction in processing time, achieving a massive 4,966x speedup. I don't mention here the I.R funcion because its a memory allocation operation and there is no improvement. Again, you can see the upgrades in the [CHANGELOG.md](docs/CHANGELOG.md) file.

## Project Structure

The project's entry point is the `main.py` file. This file is responsible for 
parsing the program's arguments and starting the reconstruction process. Object
reconstruction can be performed using any of the algorithms stored in the 
`core/complex` or `core/simple` directories.

Both algorithms make use of the abstract classes `BaseModel` and `BaseView`, 
located in the files `core/base_model.py` and `core/base_view.py`, to describe 
the reconstructed objects and their views. Once the object is reconstructed, it
is rendered using the `ModelRender` class located in `core/model_render.py`.

## Possible Improvements to Current Algorithms

It is clear that the number of objects that the current algorithms can handle is
limited due to the many constraints imposed on this project. Therefore, some 
possible improvements could include supporting objects with transverse holes and
ramps. Although the introduction stated that circular surfaces are not 
allowed—and this possibility is not listed as a future improvement—this is
because distinguishing between ramps and circular surfaces is an almost
impossible task.