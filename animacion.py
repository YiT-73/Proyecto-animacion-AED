"""Anima los eventos producidos por tabla_hash.cpp con Manim."""

from dataclasses import dataclass
from pathlib import Path

from manim import *


RUTA_EVENTOS = Path(__file__).resolve().with_name("eventos.txt")


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


@dataclass
class Paso:
    tipo: str
    tabla: list
    mensaje: str
    valor: int | None = None
    indice: int | None = None


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
            pendiente = {"valores": {v for fila in tabla for v in fila},
                         "tabla": [[] for _ in range(nueva)],
                         "mensaje": f"Rehash: {antigua} → {nueva} buckets"}
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


def crear_bucket(numero, posicion=ORIGIN):
    caja = Square(side_length=0.52, color=BLUE_B, fill_opacity=0.12)
    texto = Text(str(numero), font_size=22)
    if texto.width > 0.4:
        texto.scale_to_fit_width(0.4)
    return VGroup(caja, texto).move_to(posicion)


def crear_nodo(valor):
    circulo = Circle(radius=0.25, color=TEAL_B, fill_opacity=0.15)
    texto = Text(str(valor), font_size=20)
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
    def mensaje(self, texto):
        nuevo = Text(texto, font_size=25, color=YELLOW)
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
        contador = Text(f"Capacidad: {len(tabla)}     Elementos: {len(nodos)}",
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

    def construct(self):
        pasos = preparar_pasos(leer_eventos())
        self.titulo = Text("Tabla Hash con Chaining", font_size=36).to_edge(UP, buff=0.25)
        self.estado = Text("Tabla vacía", font_size=25, color=YELLOW).next_to(self.titulo, DOWN, buff=0.22)
        self.contador = Text("", font_size=22).to_edge(DOWN)
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


if __name__ == "__main__":
    # También permite ejecutar el archivo directamente desde el IDE.
    with tempconfig({"quality": "medium_quality", "media_dir": str(RUTA_EVENTOS.parent / "media")}):
        HashAnimation().render()
