

Dadas dos lineas 'alpha', 'beta' con los puntos 'C', 'D' y vectores 
directores 'e' y 'f' respectivamente.

- Teniendo en cuenta tambien el vector 'g = CD'. 
- Teniendo tambien 'h = ||f x g||', 'k = ||f x e||'.

Si alguno de los resultados de 'h' o 'k' es 0, no hay interseccion.
En caso contrario, continuar:

Teniendo 'l = (h/k) * e', entonces uno de los resultados de 'M = C + l'
o 'M = C - l' es la interseccion.

El signo debende de lo siguiente: si (f x g) y (f x e) apuntan en la misma 
direccion, el signo es '+', en otro caso, el signo es '-'.

Se puede comprobar si dos vectores sig