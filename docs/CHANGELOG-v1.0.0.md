
## Current developement +v1.1.0

### Eliminating double proyection - [#258a2ed](https://github.com/filipondios/object-reconstruction/commit/258a2ed8891d14ee61166552442e7c6203d49e2b)

In the first version, following the indications of the thesis of Gálvez Lamolda, J. M, each polygon contained in the model's planes was proyected to the view's plane, then converted to a 2D polygon using the view's 2D local coordinate system, then calculating the intersection of both the projected and the view's polygon. Once the result was obtained, if the intersection was empty or not a polygon (e.g a LineString), the original 3D polygon was deleted, and in the contary, this polygon is converted to 3D and then proyected to the plane where the original polygon was contained, ovewritting the original one.


```python
def refine_model(self) -> None:
    _, (plane, _) = next(iter(self.planes.items()))
    planes_normal = Matrix(plane.normal_vector)
    
    for view in self.views:        
        # ensure alignment between the view and the planes norm
        if Matrix(view.vy).cross(planes_normal).norm() > 1e-6:
            continue

        for (key, (plane, polygons)) in self.planes.items():
            refined_polygons = []

            for polygon3d in polygons:
                # Project and refine the current polygon via intersection
                projection = Polygon([view.real_to_plane(point) for point in polygon3d])
                intersection = view.polygon.intersection(projection)

                if intersection.is_empty or not isinstance(intersection, Polygon):
                    continue # Discard polygon from list

                projection = [plane.projection(view.plane_to_real(point))
                    for point in intersection.exterior.coords]
                refined_polygons.append(projection)
            self.planes[key] = (plane, refined_polygons)
```

As you can see, this is really expensive. One solution is converting the view's polygon to 3d once and then project that polygon to each plane of the model only one time and then calculate a 3D intersection between the view's polygon and each polygon in the plane. For obvious reasons, this wasnt considered by Gálvez Lamolda, J. M in his thesis, just because for his algorithm, 3D polygon insersection is way more complex than the 3D to 2D to 3D conversion.

In his algorithm, views could be not aligned with the space axes, and therefore, the model's plane could not be aligned too. This means that oventhrogh the 3D polygons are coplanar, the intersection is not trivial. Nevertheless, in this proyect's case, we only work with view's wich vision line is alined with one of the space axes, resulting in model where the planes are parallel to one of the XY, XZ, YZ space planes. 

This means that our 3D polygon intersection is trivial, because one of the 3D coordinates will be constant, resulting in a 2D-like polygon intersection, ignoring the constant coordinate. Now the const will be converting the two 3D polygons' vertices into 2D coordinates (trivial, since we only ignore one coordinate, no operations needed), calculating a 2D intersection and then converting the result 2D polygon's vertices into 3D coordinates (trivial, since we only have to add the constant coordinate that we removed before).

With this said, the model refinement function is converted to the following code.

```python
def refine_model(self) -> None:
        _, (first_plane, _) = next(iter(self.planes.items()))
        normal = Matrix(first_plane.normal_vector)
        
        # Get aligned axis
        if abs(normal[0]) > 0.99: 
            plane_axis = Axis.X
        elif abs(normal[1]) > 0.99:
            plane_axis = Axis.Y
        else: plane_axis = Axis.Z

        for view in self.views:
            # ensure alignment between the view and the planes norm
            if Matrix(view.vy).cross(normal).norm() > 1e-6:
                continue
            
            # convert view's 2D polygon to 3D
            view_polygon_3d = [view.plane_to_real(coord) 
                for coord in view.polygon.exterior.coords[:-1]]

            for (key, (plane, polygons)) in self.planes.items():
                refined_polygons = []
                
                # project the view's polygon into the plane
                view_poly_projected = [plane.projection(point) 
                    for point in view_polygon_3d]

                for polygon3d in polygons:
                    # 3D coplanar intersection
                    intersection_3d = self.intersect_3dpolygons(
                        polygon3d, view_poly_projected, plane_axis)

                    if intersection_3d: # if not empty, add
                        refined_polygons.append(intersection_3d)
                self.planes[key] = (plane, refined_polygons)
```

Now, the function wich intersects two 3D coplanar polygons is:

```python
def intersect_3dpolygons(self, poly1, poly2, axis) -> list[Point3D]:
        if axis == Axis.X:
            poly1_2d = [(p.y, p.z) for p in poly1]
            poly2_2d = [(p.y, p.z) for p in poly2]
            fixed = poly1[0].x
        
        elif axis == Axis.Y:
            poly1_2d = [(p.x, p.z) for p in poly1]
            poly2_2d = [(p.x, p.z) for p in poly2]
            fixed = poly1[0].y

        else:
            poly1_2d = [(p.x, p.y) for p in poly1]
            poly2_2d = [(p.x, p.y) for p in poly2]
            fixed = poly1[0].z

        # calculate 2d intersection
        poly1_2d = Polygon(poly1_2d)
        poly2_2d = Polygon(poly2_2d)
        intersection = poly1_2d.intersection(poly2_2d)

        if intersection.is_empty or not isinstance(intersection, Polygon):
            return []
        result3d = []

        for v in intersection.exterior.coords:
            if axis == Axis.X:   result3d.append(Point3D(fixed, v[0], v[1]))
            elif axis == Axis.Y: result3d.append(Point3D(v[0], fixed, v[1]))
            else: result3d.append(Point3D(v[0], v[1], fixed))
        return result3d
```

### Using NumPy's [numpy.array](https://numpy.org/doc/stable/reference/generated/numpy.array.html) instead of Sympy's objects

Otra limitación del programa, es el uso de los objetos [Line3D](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line3D), [Plane](https://docs.sympy.org/latest/modules/geometry/plane.html#sympy.geometry.plane.Plane), [Point3D](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point3D) y [Matrix](https://docs.sympy.org/latest/modules/matrices/dense.html#sympy.matrices.dense.Matrix) de Sympy para representar el estado del modelo. Si bien la librería ofrece funciones para intersección de líneas, planos y proyecciones de puntos en planos, estas operaciones son lentas debido a que su implementación es simbólica, no matemática, es decir, no hay una optimización en las operaciones.

La decisión inicial de usar estos objetos fue efectivamente la posibilidad de usar estas funciones y asi evitar en un primer momento la implementación de intersecciones y proyecciones. Sin embargo, el coste de tratar con estos objetos es mucho mayor que el esfuerzo de refactorizar el codigo con  NumPy [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.array.html), junto con las funciones geométricas 3D, que ahora se encuentran en el modulo `utils.geo3d`.

### Improving the Initial Reconstruction - [#5413458]()

La mejora de este método quizás no es tan evidente como las dos anteriores. Veamos primero como está organizado el codigo de esta función:

```python

# ...
d1 = view1.vy
d2 = view2.vy
# ...
segments1 = view1.rasterization_segments(common_line_point, common_line_dir, self.step, bounds)
segments2 = view2.rasterization_segments(common_line_point, common_line_dir, self.step, bounds)

axis_direction = tuple(Matrix(common_line.direction).normalized().__abs__())
axis = {(1,0,0): Axis.X, (0,1,0): Axis.Y, (0,0,1): Axis.Z}[axis_direction]

for segment1 in segments1:
    # segment1 end points
    src1 = view1.plane_to_real(segment1[0])
    dst1 = view1.plane_to_real(segment1[1])

    # get plane that contains this segment
    plane = Plane(src1, common_line.direction)
    if axis == Axis.X: key = src1.x
    elif axis == Axis.Y: key = src1.y
    elif axis == Axis.Z: key = src1.z

    if key not in self.planes:
        plane = Plane(src1, common_line.direction)
        self.planes[key] = (plane, [])
    polygon_list = self.planes[key][1]

    for segment2 in segments2:
        # check if segment2 shares plane
        src2 = view2.plane_to_real(segment2[0])
        if src2 not in plane:
            continue

        # create polygon given by the intersection of
        # lines that pass through each end point
        dst2 = view2.plane_to_real(segment2[1])        
        polygon_list.append([
            geo3d.intersect_lines(src1, d1, src2, d2),
            geo3d.intersect_lines(src1, d1, dst2, d2),
            geo3d.intersect_lines(dst1, d1, dst2, d2),
            geo3d.intersect_lines(dst1, d1, src2, d2),
        ])
# ...
```

### Aligned Axis

El primer problema aqui es la constante comprobación ineficiente de que axis está alineado con la normal de los planos del modelo para obtener una coordenada (x, y o z) como clave del diccinario de `v -> (plane, polygons)`, donde ***v*** es el valor de una coordenada. En el peor caso, se hacen 2 comprobaciones `if` comparando valores por iteración, cuando se podría simplemente calcular un indice ``[0-2]`` para `src1` ahora que es un array de NumPy de 3 posiciones y no un objeto *Vector3D* con campos (x, y, z), siendo instantáneo.

### Avoiding O(n<sup>2</sup>)

Como puedes ver, en el peor caso de tener `n` y `m` segmentos en las colecciones *segments1* y *segments2*, la complejidad será del orden O(n*m) = O(n<sup>2</sup>). Esto se debe principalmente a que por cada *segment1*, se iteran todos los *segments2*, comprobando si *src* está contenido en el mismo plano que el primer segmento, lo cual no se cumple en la mayoría de casos.

La solución fué por tanto crear un nuevo diccionario antes del bucle principal, agrupando los *segment2* por planos, sin tener que hacer verificaciones, y sabiendo que los pares de segmentos están contenidos en el mismo plano. De esta forma, se obtiene una solución O(n + m), como se puede ver:

```python
# ...
segments1 = view1.rasterization_segments(line_point, line_dir, self.step, bounds)
segments2 = view2.rasterization_segments(line_point, line_dir, self.step, bounds)

# Calculate the axis aligned with the common line
abs_dir = np.abs(line_dir)
axis_idx = int(np.argmax(abs_dir))

# direction vectors
d1 = view1.vy
d2 = view2.vz
plane_normal = line_dir

# pregroup segments by their axis-aligned
segments2_dict: dict[float, list] = {}
for seg in segments2:
    src = view2.plane_to_real(seg[0])
    key = float(src[axis_idx])
    segments2_dict.setdefault(key, []).append((src, seg[1]))

for segment1 in segments1:
    # get segment1 end points
    src1 = view1.plane_to_real(segment1[0])
    dst1 = view1.plane_to_real(segment1[1])
    key = float(src1[axis_idx])

    if key not in self.planes:
        plane_point = src1.copy()
        self.planes[key] = (plane_point, plane_normal, [])

    # get poly list and coplanar segments2
    polygon_list = self.planes[key][2]
    matching = segments2_dict.get(key, [])

    for (src2, seg2_end) in matching:
        dst2 = view2.plane_to_real(seg2_end)
        polygon_list.append([
            geo3d.intersect_lines(src1, d1, src2, d2),
            geo3d.intersect_lines(src1, d1, dst2, d2),
            geo3d.intersect_lines(dst1, d1, dst2, d2),
            geo3d.intersect_lines(dst1, d1, src2, d2),
        ])
```

El hecho de que la primera implementación fuese tan costosa, fue entre otras cosas debido a implementar de manera literal el procedimiento descrito por Gálvez Lamolda, J. M y la falta de tiempo para razonar mejores estrategias y en general, optimizaciones por tener una fecha de finalización establecida.

## Model Refinement: Getting rid of a useless projection - [#60ea68f](https://github.com/filipondios/object-reconstruction/commit/60ea68f796bea71a6df99a8cda935e833fe898f6)

Right now, the code for the model refinemet function is the following:

```python
for view in self.views:
    if np.linalg.norm(np.cross(view.vy, first_normal)) > 1e-6:
        continue

    view_polygon_3d = [view.plane_to_real(coord) 
        for coord in view.polygon.exterior.coords[:-1]]            
    unit_normal = first_normal / np.linalg.norm(first_normal)

    for (key, (plane_point, plane_normal, polygons)) in self.planes.items():
        view_poly_projected = [geo3d.project_point_to_plane(p,
            unit_normal, plane_point) for p in view_polygon_3d]

        refined_polygons = []
        for polygon3d in polygons:
            intersection_3d = geo3d.intersect_3dpolygons(
                polygon3d, view_poly_projected, plane_axis)

            if intersection_3d:
                refined_polygons.append(intersection_3d)
        self.planes[key] = (plane_point, plane_normal, refined_polygons)
```

Anteriormente, se trató la optimización de calcular la interseccion 3D entre cada poligono de los planos del modelo y cada una de los poligonos 3D que definen el contorno de las vistas. Sin embargo, hay algo que no sirve de nada hacer: calcular `view_poly_projected` y por tanto, `unit_normal`. Por que? Los planos del modelo son paralelos, teniendo una coordenada fija y al proyectar un punto (digamos un vertice del poligono de la vista) a cada uno de los planos, la unica coordenada que variará será aquella coordenada fija de los planos, que es ignorada en la función de intersección de poligonos 3D.

Imagina que seguimos el procedimiento sin optimizar, tomando los poligonos coplanares ``[(30,0,0),(30,1,0),(30,1,1)]`` y ``[(30,0,0),(30,2,0),(30,1,1)]`` de los que suponemos que uno de ellos es la proyeccion de la vista y cuyos planos son paralelos, con el eje X como normal. El algoritmo de intersección tomará ambos poligonos y al ver que el eje alineado es el X, omitirá dicha coordenada, formando los poligonos bidimensionales ``[(0,0),(1,0),(1,1)]`` y ``[(0,0),(2,0),(1,1)]`` y calculando su interseccion y anadiendo posteriormente la coordenada fija para obtener el poligono 3D resultante.

Lo mismo pasaría si los dos poligonos anteriores no fuesen coplanares, se omitiría esa coordenada. Y es que si nos damos cuenta, el poligono de la vista tambien está contenido en un plano, el de la misma vista. Por tanto, calcular esta proyección es inutil, pues la unica coordenada que varía tras la proyección es ignorada en la intersección. El código quedaría así.

```python
for view in self.views:
    if np.linalg.norm(np.cross(view.vy, first_normal)) > 1e-6:
        continue

    view_polygon_3d = [view.plane_to_real(coord) 
        for coord in view.polygon.exterior.coords[:-1]]            

    for (key, (plane_point, plane_normal, polygons)) in self.planes.items():
        refined_polygons = []
        for polygon3d in polygons:
            intersection_3d = geo3d.intersect_3dpolygons(
                polygon3d, view_polygon_3d, plane_axis)

            if intersection_3d:
                refined_polygons.append(intersection_3d)
        self.planes[key] = (plane_point, plane_normal, refined_polygons)
```

## Model refinement: Not converting to 3D - [#2e87093](https://github.com/filipondios/object-reconstruction/commit/2e87093277faeec30ef09c07b4358e666db6cad3)

We can optimize the model refinement function even more. Right now, we are calculating `view_polygon_3d`, that seems necessary in order to calculate the 3D polygon intersection between the view's polygon and each polygon in the model. However, what does `plane_to_real`?:

```python
def plane_to_real(self, point: np.ndarray) -> np.ndarray:
    u = self.vx * point[0]
    v = self.vz * point[1]
    return self.origin + u + v
```

Basically, converts a 2D point to a 3D point by adding the missing coordinate, that is the fixed coordinate of the view's plane. For example, imagine we have the point (2, 5) and we want to get the 3D version, and the view's plane normal is the X axis. Its very simple, you just have to do the operations above and you will have a point (x, 2, 5) as a result. What does this imply? That as we talked in the previous optimization, calculating the fixed coordinate is not necessary. 

On the other hand, we are calculating inside of `intersect_3dpolygons` the 3D to 2D transformation of the view's polygon in each iteration of the third loop. We can omit that conversion and pass the polygon's original 2D polygon instead. This means that the functions will be like this:

```python
def intersect_3dpolygons(poly1, poly2, axis):
    """ Intersect two coplanar 3D polygons """
    # poly2 is already 2D here!!
    if axis == Axis.X:
        poly1_2d = [(p[1], p[2]) for p in poly1]
        fixed = poly1[0][0]

    elif axis == Axis.Y:
        poly1_2d = [(p[0], p[2]) for p in poly1]
        fixed = poly1[0][1]

    else:
        poly1_2d = [(p[0], p[1]) for p in poly1]
        fixed = poly1[0][2]

    poly1_2d = Polygon(poly1_2d)
    intersection = poly1_2d.intersection(poly2)
    # ...
```

```python
for view in self.views:
    if np.linalg.norm(np.cross(view.vy, first_normal)) > 1e-6:
        continue

    for (key, (plane_point, plane_normal, polygons)) in self.planes.items():
        refined_polygons = []
        for polygon3d in polygons:
            intersection_3d = geo3d.intersect_3dpolygons(
                polygon3d, view.polygon, plane_axis)

            if intersection_3d:
                refined_polygons.append(intersection_3d)
        self.planes[key] = (plane_point, plane_normal, refined_polygons)
```

But this is not completely true. We cannot pass `view.polygon` just like that. That polygon has the 2D coordinate system of the plane in wich the view is contained. If we wanted to use this polygon in another orthogonal plane, some of the coordinates would not be valid and some of them wouldnt be used or other should be generated, following the formula at `plane_to_real`.

This can be obtained implementing this new method at `comples.View`, where the axis parameter indicates the direction of the target plane's normal vector:

```python
def polygon_view_to_plane(self, axis: Axis) -> list[tuple]:
    coords = np.array(self.polygon.exterior.coords, dtype=float)
    u = coords[:, 0]
    v = coords[:, 1]

    if axis == Axis.X:
        # transformation to (y, z)
        y = self.origin[1] + u * self.vx[1] + v * self.vz[1]
        z = self.origin[2] + u * self.vx[2] + v * self.vz[2]
        return list(zip(y, z))
    if axis == Axis.Y:
        # transformation to (x, z)
        x = self.origin[0] + u * self.vx[0] + v * self.vz[0]
        z = self.origin[2] + u * self.vx[2] + v * self.vz[2]
        return list(zip(x, z))
    else:
        # transformation to (x, y)
        x = self.origin[0] + u * self.vx[0] + v * self.vz[0]
        y = self.origin[1] + u * self.vx[1] + v * self.vz[1]
        return list(zip(x, y))
```

```python
for view in self.views:
    # ...
    poly_view_transform = Polygon(view.polygon_view_to_plane(plane_axis))

    for (key, (plane_point, plane_normal, polygons)) in self.planes.items():
        refined_polygons = []
        for polygon3d in polygons:
            intersection_3d = geo3d.intersect_3dpolygons(
                polygon3d, poly_view_transform, plane_axis)
            # ...
```