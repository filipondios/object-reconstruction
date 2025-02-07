Un plano se puede expresar como:
```
Ax + By + Cz + D = 0
```

Una recta que contiene un punto (x0,y0,z0) y tiene como 
vector director (ux,uy,uz) se pude parametrizar como:
```
x = x0 + t * ux |
y = y0 + t * uy |-
z = z0 + t * uz |
```

Si sustituimos (x,y,z) de la ecuacion de la recta en la del 
plano, obtenemos la siguiente expresion:

```
A(x0 + t * ux) + B(y0 + t * uy) + C(z0 + t * uz) + D = 0
```

Si despeamos para resolver t, obtenemos:
```
      Ax0 + By0 + Cz0 + D
t = - -------------------
        Aux + Buy + Cuz
```

Una vez encontrado el valor de t, lo sustituimos en la 
ecuacion de la recta, de forma que obtenemos las coordenadas
de un punto:
```
(x0 + t * ux, y0 + t * uy, z0 + t * uz)`
```