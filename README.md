# Object reconstruction

## Overview

This project aims to reconstruct simple 3D objects from their 2D orthographic projections. The program can take multiple views of the
object like its plan, profile, and elevation and then try to generate a 3D representation of the object in an orthographic space.

One limitation of the program is that objects with transversal gaps are not correctly reconstructed, as the gaps at this point are
not possible to be detected by the program.

## Docs

In case you want to read the program code and understand the steps involved, you can have a look at the wiki of this project. There you 
will find not only an explanation of the steps to follow for the reconstruction of a three-dimensional object by its orthogonal
views but also the description of the Java classes of the application and their use.
