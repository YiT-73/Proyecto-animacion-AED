from manim import *


def leer_eventos():

    eventos = []

    with open("eventos.txt") as archivo:

        for linea in archivo:

            datos = linea.strip().split()

            if datos[0] == "INSERT":

                eventos.append(
                    (
                        "INSERT",
                        int(datos[1]),
                        int(datos[2])
                    )
                )

            elif datos[0] == "REHASH":

                eventos.append(
                    (
                        "REHASH",
                        int(datos[1]),
                        int(datos[2])
                    )
                )

            elif datos[0] == "SEARCH":

                eventos.append(
                    (
                        "SEARCH",
                        int(datos[1]),
                        int(datos[2])
                    )
                )

            elif datos[0] == "REMOVE":

                eventos.append(
                    (
                        "REMOVE",
                        int(datos[1]),
                        int(datos[2])
                    )
                )

    return eventos



def crear_bucket(numero, posicion):

    caja = Square(
        side_length=0.8
    )

    texto = Text(
        str(numero)
    ).scale(0.5)

    grupo = VGroup(
        caja,
        texto
    )

    grupo.move_to(posicion)

    return grupo



def crear_nodo(valor):

    circulo = Circle(
        radius=0.25
    )

    texto = Text(
        str(valor)
    ).scale(0.35)

    nodo = VGroup(
        circulo,
        texto
    )

    return nodo



class HashAnimation(Scene):

    def construct(self):

        titulo = Text(
            "Tabla Hash con Chaining"
        )

        titulo.to_edge(UP)

        self.play(
            Write(titulo)
        )


        # -------------------------
        # Crear tabla inicial
        # -------------------------

        capacidad = 5

        buckets = []

        posiciones = []


        for i in range(capacidad):

            pos = RIGHT*(i-2)*1.2

            posiciones.append(pos)

            bucket = crear_bucket(
                i,
                pos
            )

            buckets.append(bucket)


        self.play(
            Create(
                VGroup(*buckets)
            )
        )


        # Guarda los nodos por bucket
        # Ejemplo:
        # tabla[3] = [nodo1,nodo2,nodo3]

        tabla = {
            i:[]
            for i in range(capacidad)
        }


        eventos = leer_eventos()


        # Guarda flechas del chaining

        enlaces = []



        for evento in eventos:


            tipo = evento[0]


            # -------------------------
            # INSERT
            # -------------------------

            if tipo == "INSERT":


                valor = evento[1]
                indice = evento[2]


                nodo = crear_nodo(
                    valor
                )


                cantidad = len(
                    tabla[indice]
                )


                # posición del nodo
                # sale hacia la derecha

                nodo.move_to(
                    posiciones[indice]
                )


                nodo.shift(
                    RIGHT*(cantidad+1)*0.8
                )


                self.play(
                    Create(nodo)
                )


                # Crear flecha si ya había elementos

                if cantidad > 0:

                    anterior = tabla[indice][-1]

                    flecha = Arrow(
                        anterior.get_right(),
                        nodo.get_left(),
                        buff=0.05
                    )

                    enlaces.append(
                        flecha
                    )

                    self.play(
                        Create(flecha)
                    )


                tabla[indice].append(
                    nodo
                )


                self.wait(0.5)



            # -------------------------
            # REHASH
            # -------------------------

            elif tipo == "REHASH":


                antigua = evento[1]
                nueva = evento[2]

                tabla = {
                    i: []
                    for i in range(nueva)
                }

                capacidad = nueva

                posiciones = []

                for i in range(nueva):
                    posiciones.append(
                        RIGHT*(i-nueva/2)*0.8
                    )

                texto = Text(
                    f"REHASH: {antigua} -> {nueva}"
                )

                texto.next_to(
                    titulo,
                    DOWN
                )


                self.play(
                    Write(texto)
                )


                self.wait(1)


                self.play(
                    FadeOut(texto)
                )



            # -------------------------
            # SEARCH
            # -------------------------

            elif tipo == "SEARCH":


                valor = evento[1]

                texto = Text(
                    f"Buscar: {valor}"
                )

                texto.next_to(
                    titulo,
                    DOWN
                )


                self.play(
                    Write(texto)
                )


                self.wait(1)


                self.play(
                    FadeOut(texto)
                )



            # -------------------------
            # REMOVE
            # -------------------------

            elif tipo == "REMOVE":


                valor = evento[1]


                texto = Text(
                    f"Eliminar: {valor}"
                )

                texto.next_to(
                    titulo,
                    DOWN
                )


                self.play(
                    Write(texto)
                )


                self.wait(1)


                self.play(
                    FadeOut(texto)
                )


        self.wait(2)