# Proyecto de animación AED

Visualización con Manim de la tabla hash con encadenamiento de `tabla_hash.cpp`.
Los buckets se muestran en vertical y cada cadena crece hacia la derecha.
La animación conserva el orden de inserción en cabeza, muestra el rehash,
recorre las cadenas al buscar y retira los nodos al eliminar.

Desde la carpeta del proyecto, con Manim instalado en `venv`:

```bash
g++ -std=c++17 tabla_hash.cpp -o hash
./hash
venv/bin/python -m manim -qm animacion.py HashAnimation
```

El video queda en `media/videos/animacion/720p30/HashAnimation.mp4`.
Para una vista previa rápida, cambia `-qm` por `-ql` (salida en `480p15`).
También puedes ejecutar `venv/bin/python animacion.py` desde el IDE para renderizar.
El archivo de eventos se busca junto a `animacion.py`, independientemente del
directorio desde el que se invoque Python.

Vuelve a compilar y ejecutar C++ cuando cambies la demostración. El ejecutable
anterior puede generar un registro antiguo que no incluye las reubicaciones.

El registro utiliza `INIT capacidad` para iniciar cada tabla; `INSERT`, `SEARCH`
y `REMOVE` incluyen clave e índice (o `NOT FOUND` para operaciones fallidas).
`REHASH antigua nueva` va seguido por un `MOVE clave índice` por cada nodo y
`REHASH_END`. Así se utilizan los destinos calculados por la función hash de
C++, incluso para multiplicación o hashing universal. Los registros antiguos
con rehash deben regenerarse porque no contienen esos destinos.

Pruebas de lectura, operaciones y distribución visual:

```bash
venv/bin/python -m unittest -v test_animacion.py
```
