# Object Reconstruction

> [!NOTE]  
> This repository also contains a README in Spanish.  
> If you prefer to read the documentation in Spanish, please refer to this [README](README_ES.md).

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

| Step (units) | I.R (s) | M.R (s) | Planes (units) | Polygons (units)  | Vertices (units) |
|--------------|---------|---------|----------------|-------------------|------------------|
| 8            | 0.517   | 3.3578  | 17             | 19                | 115              |
| 7            | 0.4541  | 3.0368  | 18             | 17                | 105              |
| 6            | 0.4834  | 3.644   | 20             | 20                | 128              |
| 5            | 1.0824  | 7.1731  | 30             | 45                | 253              |
| 4            | 1.0199  | 7.086   | 32             | 41                | 245              |
| 3            | 1.1253  | 8.142   | 39             | 46                | 286              |
| 2            | 2.0125  | 12.3338 | 60             | 69                | 425              |
| 1            | 5.5638  | 24.0606 | 118            | 133               | 821              |
| 0.5          | 16.313  | 44.7234 | 228            | 243               | 1531             |

Results for the simplified (voxel-based) algorithm implementation:

| Resolution (units) | I.R (s)    | M.R (s)   | Total Voxels  | Active Voxels  | Active %  |
|--------------------|------------|-----------|---------------|----------------|-----------|
| 8                  | 2.51E-05   | 0.1259    | 512           | 52             | 10.1563   |
| 16                 | 1.93E-05   | 0.481     | 4096          | 294            | 7.1777    |
| 24                 | 2.22E-05   | 1.0699    | 13824         | 1144           | 8.2755    |
| 32                 | 2.56E-05   | 1.9026    | 32768         | 2576           | 7.8613    |
| 48                 | 5.41E-05   | 4.2783    | 110592        | 8544           | 7.7257    |
| 64                 | 8.81E-05   | 7.6205    | 262144        | 22174          | 8.4587    |
| 96                 | 0.00028391 | 17.1236   | 884736        | 70784          | 8.0006    |
| 128                | 0.00032687 | 30.3715   | 2097152       | 167112         | 7.9685    |

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

## Creating New Reconstruction Algorithms

### The BaseModel Class

As explained in the previous section, all algorithms in this project use the 
`BaseModel` and `BaseView` classes. The `BaseModel` class contains abstract 
methods that define each stage of the reconstruction process, which must be
overridden by specific reconstruction algorithms. It also includes a method to 
draw the reconstructed object in 3D space and another to display additional 
information after reconstruction.

```python
class BaseModel:

  def __init__(self, path: str, print_info: bool, viewClass: BaseView)
    # Initialization of other properties...
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

As shown, the constructor of the ``BaseModel`` class calls the three 
reconstruction functions in sequence and optionally displays extra information. 
The draw_model method is used in the ModelRender class to render the 3D model 
using the raylib library.

> [!TIP]  
> The `BaseModel` class includes additional attributes that provide more 
> information. These include: A list of views of the object and a tuple that
> stores the dimensions or bounding box enclosing the actual object. For more
> details, see the [BaseModel](core/base_model.py) class.

### The BaseView Class

The idea behind the `BaseView` class is to store all the information related to 
a view of the model. This includes the position and orientation of the camera 
used to take an image of the object to be reconstructed, represented by three 
vectors `Vx`, `Vy`, `Vz` and a point `O`, as illustrated below:

<div align='center'>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/25266148-5bb3-4982-a6d1-bd185c790d0d" />
</div>

In addition to the camera information, it stores the 2D polyline (list of points)
that defines the contour of the object's projection, i.e., the view's image.
Although the polyline of the view's contour is obtained, internal polygons that 
might define transverse holes are not.

The `BaseView` class also includes a method that allows projecting 3D points
onto the view plane and converting them into 2D coordinates relative to the 
origin `O` of the view, and another method that converts 2D coordinates back 
into 3D coordinates.

```python
class BaseView:

  def __init__(self, path: Path):
    # Initializes Vx, Vy, Vz, O

  def plane_to_real(self, point: tuple[float, float]):
    # Converts a 2D point to 3D

  def real_to_plane(self, point: tuple[float, float, float]):
    # Converts a 3D point to 2D
```

These methods are very useful during the reconstruction process, as they are 
frequently used in classes that inherit from `BaseModel`. Unlike `BaseModel`,
`BaseView` already contains almost all the necessary information, so it is 
common for new algorithms to use `BaseView` directly rather than inherit from it.

### Integrating the New Algorithm

Once the developer has created a new reconstruction algorithm using the 
`BaseModel` class, it can be integrated by adding a new option to the 
`--complexity` parameter in `main.py`. The necessary arguments must also be 
passed to the new reconstruction algorithm in this file.

> [!NOTE]  
> In future versions of the program, functionality might be added to make it 
> easier to integrate new algorithms automatically without modifying the 
> `main.py` file. In the meantime, the manual approach must be used.

## Creating New Objects

In the `examples/` directory, you can find several objects along with their 
corresponding views. A model is composed of a series of subdirectories, each
describing a view. Each view must contain a `camera.json` file that defines the
orientation and position of the camera, as well as the orthogonal projection of
the object for that camera configuration in the `plane.bmp` file.

The contents of the `camera.json` file simply represent the attributes of a 
`BaseView` object. For example, a file describing the position and orientation
of the camera might look like this:

```json
{
  "name": "elevation",
  "origin": [40, 0, 0],
  "vx": [0, -1, 0],
  "vy": [-1, 0, 0],
  "vz": [0, 0, 1]
}
```

> [!NOTE]  
> The `Vx`, `Vy`, and `Vz` vectors must be normalized to avoid potential errors 
> in the reconstruction methods. These vectors are not normalized automatically
> when loaded into a `BaseView` object.

On the other hand, the object projections stored in the `plane.bmp` images must 
follow the expected format to correctly extract the polyline that defines the 
projection contour: The background should be white (`255`), the figure's edges 
should be black (`0`), and the inner area of the figure can be filled with any 
other RGB color.
