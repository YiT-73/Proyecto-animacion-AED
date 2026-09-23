"""Explica las tablas hash y anima los eventos de tabla_hash.cpp con Manim."""

from dataclasses import dataclass
from pathlib import Path

from manim import *


RUTA_EVENTOS = Path(__file__).resolve().with_name("eventos.txt")
DURACION_MINIMA = 60  # Segundos, incluso si se usa un registro más corto.


@dataclass
class Paso:
    tipo: str
    tabla: list
    mensaje: str
    valor: int | None = None
    indice: int | None = None


def leer_eventos(ruta=RUTA_EVENTOS):
    eventos = []
    with Path(ruta).open(encoding="utf-8") as archivo:
        for numero, linea in enumerate(archivo, 1):
            datos = linea.split()
            if not datos or datos[0].startswith("#"):
                continue
            tipo = datos[0]
            try:
                if tipo == "INIT" and len(datos) == 2:
                    evento = (tipo, int(datos[1]))
                elif tipo == "REHASH_END" and len(datos) == 1:
                    evento = (tipo,)
                elif tipo in {"SEARCH", "REMOVE"} and datos[2:] == ["NOT", "FOUND"]:
                    evento = (tipo, int(datos[1]), None)
                elif tipo in {"INSERT", "SEARCH", "REMOVE", "REHASH", "MOVE"} and len(datos) == 3:
                    evento = (tipo, int(datos[1]), int(datos[2]))
                else:
                    raise ValueError("evento desconocido o incompleto")
            except (ValueError, IndexError) as error:
                raise ValueError(f"{ruta}, línea {numero}: {linea.strip()}") from error
            eventos.append(evento)
    return eventos


def preparar_pasos(eventos):
    """Valida el registro antes de renderizar y conserva el orden de las listas."""
    tabla = [[] for _ in range(5)]  # Capacidad predeterminada para registros sin INIT.
    pasos = []
    pendiente = None

    def guardar(tipo, mensaje, valor=None, indice=None):
        pasos.append(Paso(tipo, [fila.copy() for fila in tabla], mensaje, valor, indice))

    for evento in eventos:
        tipo = evento[0]
        if pendiente is not None and tipo not in {"MOVE", "REHASH_END"}:
            raise ValueError("Rehash incompleto: faltan MOVE o REHASH_END. Regenera eventos.txt.")
        if tipo == "INIT":
            capacidad = evento[1]
            if capacidad <= 0:
                raise ValueError("La capacidad debe ser positiva.")
            tabla = [[] for _ in range(capacidad)]
            guardar(tipo, "Tabla vacía · inserción al inicio de cada cadena")
        elif tipo == "REHASH":
            antigua, nueva = evento[1:]
            if antigua != len(tabla) or nueva <= antigua:
                raise ValueError("Capacidades inconsistentes. Regenera eventos.txt con tabla_hash.cpp.")
            pendiente = {
                "valores": {v for fila in tabla for v in fila},
                "tabla": [[] for _ in range(nueva)],
                "mensaje": f"Rehash: {antigua} → {nueva} buckets",
            }
        elif tipo == "MOVE":
            valor, indice = evento[1:]
            if pendiente is None or valor not in pendiente["valores"]:
                raise ValueError(f"Reubicación inválida para {valor}.")
            if not 0 <= indice < len(pendiente["tabla"]):
                raise ValueError(f"Bucket inválido: {indice}.")
            pendiente["tabla"][indice].insert(0, valor)
            pendiente["valores"].remove(valor)
        elif tipo == "REHASH_END":
            if pendiente is None or pendiente["valores"]:
                raise ValueError("El rehash no reubicó todos los elementos.")
            tabla = pendiente["tabla"]
            guardar("REHASH", pendiente["mensaje"])
            pendiente = None
        else:
            valor, indice = evento[1:]
            if indice is None:
                if any(valor in fila for fila in tabla):
                    raise ValueError(f"El registro dice que {valor} no existe, pero está en la tabla.")
                guardar(tipo, f"{'Buscar' if tipo == 'SEARCH' else 'Eliminar'} {valor}: no encontrado", valor)
                continue
            if not 0 <= indice < len(tabla):
                raise ValueError(f"Bucket inválido: {indice}.")
            if tipo == "INSERT":
                existente = next((i for i, fila in enumerate(tabla) if valor in fila), None)
                if existente is not None and existente != indice:
                    raise ValueError("El registro mezcla tablas distintas. Regenera eventos.txt.")
                if existente is None:
                    tabla[indice].insert(0, valor)
                guardar(tipo, f"{'Insertar' if existente is None else 'Actualizar'} {valor} · bucket {indice}", valor, indice)
            elif tipo in {"SEARCH", "REMOVE"}:
                if valor not in tabla[indice]:
                    raise ValueError(f"{valor} no está en el bucket {indice} indicado por {tipo}.")
                if tipo == "REMOVE":
                    tabla[indice].remove(valor)
                guardar(tipo, f"{'Buscar' if tipo == 'SEARCH' else 'Eliminar'} {valor} · bucket {indice}", valor, indice)
            else:
                raise ValueError(f"Evento no reconocido: {tipo}.")
    if pendiente is not None:
        raise ValueError("Rehash incompleto. Regenera eventos.txt con tabla_hash.cpp.")
    return pasos


def crear_texto(contenido, **estilo):
    estilo.setdefault("font", "Arial")
    estilo.setdefault("disable_ligatures", True)
    estilo.setdefault("line_spacing", 0.35)
    texto = Text(contenido, **estilo)
    if texto.width > config.frame_width - 1.4:
        texto.scale_to_fit_width(config.frame_width - 1.4)
    return texto


def crear_bucket(numero, posicion=ORIGIN):
    caja = Square(side_length=0.52, color=BLUE_B, fill_opacity=0.12)
    texto = crear_texto(str(numero), font_size=22)
    if texto.width > 0.4:
        texto.scale_to_fit_width(0.4)
    return VGroup(caja, texto).move_to(posicion)


def crear_nodo(valor):
    circulo = Circle(radius=0.25, color=TEAL_B, fill_opacity=0.15)
    texto = crear_texto(str(valor), font_size=20)
    if texto.width > 0.4:
        texto.scale_to_fit_width(0.4)
    return VGroup(circulo, texto)


def crear_tabla(tabla):
    buckets, nodos, enlaces = {}, {}, VGroup()
    for indice, fila in enumerate(tabla):
        posicion = DOWN * indice * 0.66
        bucket = crear_bucket(indice, posicion)
        buckets[indice] = bucket
        anterior = bucket
        for orden, valor in enumerate(fila):
            nodo = crear_nodo(valor).move_to(posicion + RIGHT * (orden + 1) * 1.05)
            nodos[valor] = nodo
            enlaces.add(Arrow(anterior.get_right(), nodo.get_left(), buff=0.06,
                              stroke_width=2, max_tip_length_to_length_ratio=0.2))
            anterior = nodo
    grupo = VGroup(*buckets.values(), *nodos.values(), enlaces)
    escala = min(1, (config.frame_width - 1.4) / grupo.width,
                 (config.frame_height - 2.7) / grupo.height)
    grupo.scale(escala).move_to(DOWN * 0.5)
    return buckets, nodos, enlaces


class HashAnimation(Scene):
    def construct(self):
        pasos = preparar_pasos(leer_eventos())
        self.mostrar_portada()
        self.explicar_funcionamiento()
        self.explicar_tipos_hash()
        self.explicar_complejidad()
        self.mostrar_demo(pasos)

        # La demo habitual supera el minuto con la explicación inicial.
        # Si se acortan los eventos, se conserva la tabla final el tiempo restante.
        if self.time < DURACION_MINIMA:
            self.wait(DURACION_MINIMA - self.time)

    def limpiar_pantalla(self):
        self.play(*[FadeOut(objeto) for objeto in self.mobjects], run_time=0.6)

    def mostrar_portada(self):
        titulo = crear_texto(
            "Funcionamiento de la tabla hash", font_size=44, weight=BOLD,
        )
        curso = crear_texto(
            "Curso: Algoritmos y Estructuras de Datos", font_size=27,
        )
        encabezado = VGroup(titulo, curso).arrange(DOWN, buff=0.55)
        integrantes = VGroup(
            crear_texto("Integrantes:", font_size=27, color=BLUE_B),
            crear_texto("Yitzhak Abraham Namihas Millan", font_size=25),
            crear_texto("Carla Viviana Molina Álvarez", font_size=25),
        ).arrange(DOWN, buff=0.3)
        VGroup(encabezado, integrantes).arrange(DOWN, buff=0.85).move_to(ORIGIN)
        self.play(FadeIn(encabezado), FadeIn(integrantes), run_time=0.4)
        self.wait(2)
        self.limpiar_pantalla()

    def explicar_tipos_hash(self):
        titulo = crear_texto("Tres métodos de hash", font_size=36).to_edge(UP)
        variables = crear_texto(
            "x = hash(clave) · m = cantidad de buckets", font_size=23,
        ).next_to(titulo, DOWN, buff=0.3)
        metodos = [
            (
                "División",
                "h(clave) = x mod m",
                "Usa el resto de dividir x entre m como índice del bucket.",
                BLUE_B, 6,
            ),
            (
                "Multiplicación",
                "h(clave) = piso(m × frac(x × A)), 0 < A < 1",
                "Toma la parte decimal de x × A, la multiplica por m\n"
                "y redondea hacia abajo para obtener el índice.",
                TEAL_B, 8,
            ),
            (
                "Universal",
                "h(clave) = ((a × x + b) mod p) mod m",
                "Elige a entre 1 y p − 1 y b entre 0 y p − 1 una vez al azar.\n"
                "Con p primo, mezcla x y aplica módulo p y luego módulo m.",
                GREEN, 9,
            ),
        ]
        bloques = VGroup()
        for nombre, formula, descripcion, color, _ in metodos:
            bloque = VGroup(
                crear_texto(nombre, font_size=27, color=color),
                crear_texto(formula, font_size=23, font="Consolas"),
                crear_texto(descripcion, font_size=21, color=GREY_B),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
            bloques.add(bloque)
        bloques.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        if bloques.width > config.frame_width - 1.4:
            bloques.scale_to_fit_width(config.frame_width - 1.4)
        if bloques.height > 4.8:
            bloques.scale_to_fit_height(4.8)
        bloques.move_to(DOWN * 0.35)

        self.play(Write(titulo), FadeIn(variables), run_time=1)
        for bloque, metodo in zip(bloques, metodos):
            self.play(FadeIn(bloque), run_time=0.8)
            self.wait(metodo[4])

        eleccion = crear_texto(
            "En este video usamos el hash por división.",
            font_size=27, color=YELLOW,
        ).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(eleccion), run_time=1)
        self.wait(4)
        self.limpiar_pantalla()

    def explicar_funcionamiento(self):
        titulo = crear_texto("¿Cómo funciona una tabla hash?", font_size=36).to_edge(UP)
        descripcion = crear_texto(
            "Guarda pares clave–valor y usa la clave para localizar un bucket.",
            font_size=25,
        ).next_to(titulo, DOWN, buff=0.45)
        formula = VGroup(
            crear_texto("Hash por división", font_size=25, color=YELLOW),
            crear_texto(
                "h(clave) = hash(clave) mod m", font_size=25, font="Consolas",
            ),
        ).arrange(DOWN, buff=0.18).move_to(UP * 1.5)
        capacidad = crear_texto("m es la cantidad de buckets", font_size=22, color=GREY_B)
        capacidad.next_to(formula, DOWN, buff=0.25)

        self.play(Write(titulo), FadeIn(descripcion), run_time=1.2)
        self.play(Write(formula), FadeIn(capacidad), run_time=1)
        self.wait(4)

        ejemplo = VGroup(
            crear_texto("Ejemplo con m = 5 y hash(clave) = clave", font_size=22),
            crear_texto("3 mod 5 = 3", font_size=24, font="Consolas"),
        ).arrange(DOWN, buff=0.18).move_to(UP * 0.05)
        bucket = crear_bucket(3).move_to(LEFT * 1.4 + DOWN * 0.9)
        nodo_8 = crear_nodo(8).next_to(bucket, RIGHT, buff=0.7)
        nodo_3 = crear_nodo(3).next_to(nodo_8, RIGHT, buff=0.7)
        enlace_8 = Arrow(bucket.get_right(), nodo_8.get_left(), buff=0.06)
        enlace_3 = Arrow(nodo_8.get_right(), nodo_3.get_left(), buff=0.06)
        posicion_3 = nodo_3.get_center().copy()
        nodo_3.move_to(nodo_8)
        self.play(FadeIn(ejemplo), FadeIn(bucket), FadeIn(nodo_3), Create(enlace_8))
        self.wait(4)

        colision = crear_texto(
            "8 mod 5 también da 3: hay una colisión.", font_size=25, color=YELLOW,
        ).move_to(DOWN * 1.65)
        encadenamiento = crear_texto(
            "Chaining: las claves del mismo bucket forman una lista enlazada.",
            font_size=24,
        ).next_to(colision, DOWN, buff=0.3)
        operaciones = crear_texto(
            "Insertar agrega al inicio; buscar y eliminar recorren esa lista.",
            font_size=24,
        ).next_to(encadenamiento, DOWN, buff=0.3)
        self.play(nodo_3.animate.move_to(posicion_3), run_time=0.5)
        self.play(FadeIn(nodo_8), Create(enlace_3), FadeIn(colision))
        self.play(FadeIn(encadenamiento), FadeIn(operaciones))
        self.wait(6)
        self.limpiar_pantalla()

    def explicar_complejidad(self):
        titulo = crear_texto("¿Cuánto cuesta cada operación?", font_size=36).to_edge(UP)
        formula = VGroup(
            crear_texto("Tiempo esperado: O(1 + α)", font_size=27, color=YELLOW),
            crear_texto("α = n / m", font_size=27, color=YELLOW, font="Consolas"),
        ).arrange(RIGHT, buff=0.65).next_to(titulo, DOWN, buff=0.35)
        condicion = crear_texto(
            "n: elementos · m: buckets · O(1) con buena distribución y carga α acotada",
            font_size=22,
        ).next_to(formula, DOWN, buff=0.25)
        self.play(Write(titulo), FadeIn(formula), FadeIn(condicion), run_time=1.5)
        self.wait(4)

        # Text mantiene la gráfica independiente de una instalación de LaTeX.
        ejes = Axes(
            x_range=[0, 10, 2], y_range=[0, 10, 2],
            x_length=5.5, y_length=2.8,
            axis_config={"include_tip": False, "color": GREY_B},
        ).move_to(LEFT * 3 + DOWN * 0.4)
        etiqueta_x = crear_texto("Cantidad de elementos (n)", font_size=19)
        etiqueta_x.next_to(ejes, DOWN, buff=0.2)
        etiqueta_y = crear_texto("Tiempo relativo", font_size=19)
        etiqueta_y.next_to(ejes, UP, buff=0.15)
        constante = ejes.plot(lambda n: 1, x_range=[0, 10], color=GREEN)
        lineal = ejes.plot(lambda n: n, x_range=[0, 10], color=RED)
        leyenda = VGroup(
            crear_texto("Tiempo esperado por operación", font_size=23, color=GREEN),
            crear_texto("Inserción: O(1) amortizado", font_size=23),
            crear_texto("Búsqueda: O(1)", font_size=23),
            crear_texto("Eliminación: O(1)", font_size=23),
            crear_texto("Peor caso: O(n) por operación", font_size=23, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        if leyenda.width > 5.7:
            leyenda.scale_to_fit_width(5.7)
        leyenda.move_to(RIGHT * 3.3 + DOWN * 0.3)
        self.play(Create(ejes), FadeIn(etiqueta_x), FadeIn(etiqueta_y))
        self.play(Create(constante), FadeIn(leyenda[:4]), run_time=1.5)
        self.wait(3)
        self.play(Create(lineal), FadeIn(leyenda[4]), run_time=1.5)
        self.wait(4)

        rehash = crear_texto(
            "Rehash: O(m + n) al redistribuir; inserción esperada amortizada: O(1).",
            font_size=23, color=YELLOW,
        ).move_to(DOWN * 2.7)
        self.play(FadeIn(rehash))
        self.wait(5)
        self.limpiar_pantalla()

    def mostrar_demo(self, pasos):
        self.titulo = crear_texto("Tabla Hash con Chaining", font_size=36).to_edge(UP, buff=0.25)
        self.estado = crear_texto("Tabla vacía", font_size=25, color=YELLOW).next_to(self.titulo, DOWN, buff=0.22)
        self.contador = crear_texto("", font_size=22).to_edge(DOWN)
        self.buckets, self.nodos, self.enlaces = {}, {}, VGroup()
        self.tabla = []
        self.play(Write(self.titulo), FadeIn(self.estado))
        if not pasos or pasos[0].tipo != "INIT":
            self.actualizar_tabla([[] for _ in range(5)])
        for paso in pasos:
            self.mensaje(paso.mensaje)
            if paso.tipo in {"SEARCH", "REMOVE"}:
                self.recorrer(paso)
            if paso.tipo == "INIT":
                objetos = [*self.buckets.values(), *self.nodos.values(), *self.enlaces]
                if objetos:
                    self.play(*[FadeOut(objeto) for objeto in objetos], run_time=0.4)
                self.buckets, self.nodos, self.enlaces = {}, {}, VGroup()
            if paso.tipo in {"INIT", "INSERT", "REHASH", "REMOVE"}:
                self.actualizar_tabla(paso.tabla)
            if paso.tipo == "INSERT":
                self.play(Indicate(self.nodos[paso.valor], color=GREEN), run_time=0.4)
            elif paso.tipo == "SEARCH" and paso.indice is not None:
                self.mensaje(f"Buscar {paso.valor}: encontrado en el bucket {paso.indice}")
            self.wait(0.45)
        self.wait(2)

    def mensaje(self, texto):
        nuevo = crear_texto(texto, font_size=25, color=YELLOW)
        if nuevo.width > config.frame_width - 1:
            nuevo.scale_to_fit_width(config.frame_width - 1)
        nuevo.next_to(self.titulo, DOWN, buff=0.22)
        self.play(Transform(self.estado, nuevo), run_time=0.3)

    def actualizar_tabla(self, tabla):
        buckets, nodos, enlaces = crear_tabla(tabla)
        # Retirar los enlaces antes de mover sus extremos evita flechas sueltas.
        if len(self.enlaces):
            self.play(FadeOut(self.enlaces), run_time=0.15)
        animaciones = []
        for actuales, nuevos in ((self.buckets, buckets), (self.nodos, nodos)):
            for clave, objeto in actuales.items():
                if clave in nuevos:
                    animaciones.append(Transform(objeto, nuevos[clave]))
                    nuevos[clave] = objeto
                else:
                    animaciones.append(FadeOut(objeto))
            for clave, objeto in nuevos.items():
                if clave not in actuales:
                    animaciones.append(FadeIn(objeto))
        self.play(*animaciones, run_time=0.65)
        if len(enlaces):
            self.play(Create(enlaces), run_time=0.25)
        self.buckets, self.nodos, self.enlaces = buckets, nodos, enlaces
        self.tabla = [fila.copy() for fila in tabla]
        contador = crear_texto(f"Capacidad: {len(tabla)}     Elementos: {len(nodos)}",
                        font_size=22, color=GREY_B).to_edge(DOWN, buff=0.22)
        self.play(Transform(self.contador, contador), run_time=0.2)

    def recorrer(self, paso):
        if paso.indice is None:
            return
        self.play(Indicate(self.buckets[paso.indice], color=YELLOW), run_time=0.45)
        for valor in self.tabla[paso.indice]:
            self.play(Indicate(self.nodos[valor], color=GREEN if valor == paso.valor else YELLOW),
                      run_time=0.45)
            if valor == paso.valor:
                break


if __name__ == "__main__":
    # También permite ejecutar el archivo directamente desde el IDE.
    with tempconfig({"quality": "medium_quality", "media_dir": str(RUTA_EVENTOS.parent / "media")}):
        HashAnimation().render()
