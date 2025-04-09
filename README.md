# Object reconstruction

## Overview

This project aims to reconstruct simple three-dimensional objects from their orthogonal projections represented as images.

> [!NOTE]
> As a limitation of the program, the objects to be reconstructed must not have ramps, transverse holes, or curved surfaces. All faces of the object must be flat, and the normal vector of the plane containing them must align with the direction of one of the coordinate axes. Additionally, the line of sight of the projections (images) must also align with one of the coordinate axes, resulting in six possible views of the object. It is important to clarify that the three spatial axes must be mutually perpendicular, forming 90-degree angles with each other.

To achieve this, two algorithms are compared. The first is part of the original algorithm by José M. Gálvez Lamolda, used in his doctoral thesis <a href="https://accedacris.ulpgc.es/handle/10553/21247">*Reconstruction of Objects from Two-Dimensional Views and Their Recognition Using 3D Moments*</a>, which reconstructs objects from any point in space without restrictions on the viewing direction or object shape. The second is a derivative algorithm developed by me, adapted to the constraints imposed by this specific problem.

## Examples

Currently, only the algorithm derived from the original is implemented, located in the <a href="derived-method">derived-method folder</a>, while the original algorithm is still under development in the <a href="original-method">original-method</a> directory. Some results for objects reconstructed using their top, front, and side views are shown below:

<div align="center">
  <img width=180 src="https://github.com/user-attachments/assets/6a3c7800-9bf8-404c-b00b-93ed69d8294e">
  <img width=180 src="https://github.com/user-attachments/assets/5e0038c4-9713-4293-8133-1f5a40ccf079">
  <img width=180 src="https://github.com/user-attachments/assets/3d2350e2-4253-4982-9e5e-63fd0e4aa208">
  <img width=180 src="https://github.com/user-attachments/assets/59cbb0f2-d964-447d-ad99-7e222d4fbdd5">
</div>

<div align="center">
  <img width=180 src="https://github.com/user-attachments/assets/6db6c51a-3eec-4be8-8cdc-aa31c815e686">
  <img width=180 src="https://github.com/user-attachments/assets/37b3a029-9157-403b-b278-5cdcf1a91585">
  <img width=180 src="https://github.com/user-attachments/assets/5fd4ce6e-f725-4fe6-b6bb-5b7cf1ae2f27">
  <img width=180 src="https://github.com/user-attachments/assets/7b7938aa-f4eb-4f86-8364-5fe69971b3d7">
</div>

## Compile and run the project

To run this project you will need [maven](https://maven.apache.org/). Then, run the program with one command:

```bash
mvn -q clean compile && mvn -q exec:java -Dexec.mainClass="com.app.Main"
```
