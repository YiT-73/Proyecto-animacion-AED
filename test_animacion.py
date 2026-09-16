import tempfile
import unittest
from pathlib import Path

from animacion import crear_tabla, leer_eventos, preparar_pasos
from manim import VGroup, config, tempconfig


class EventosTest(unittest.TestCase):
    def test_lectura_lineas_vacias_y_busquedas_fallidas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "eventos.txt"
            ruta.write_text("\n# ejemplo\nINIT 5\nSEARCH 8 NOT FOUND\nREMOVE 8 NOT FOUND\n")
            pasos = preparar_pasos(leer_eventos(ruta))
            self.assertEqual(pasos[-1].tabla, [[] for _ in range(5)])
            self.assertIn("no encontrado", pasos[-2].mensaje)
            ruta.write_text("\nINSERT x 2\n")
            with self.assertRaisesRegex(ValueError, "línea 2"):
                leer_eventos(ruta)

    def test_colisiones_rehash_y_eliminacion(self):
        # MOVE define el destino real, incluso si la función no es módulo.
        pasos = preparar_pasos([
            ("INIT", 2), ("INSERT", 4, 0), ("INSERT", 8, 0),
            ("REHASH", 2, 4), ("MOVE", 8, 3), ("MOVE", 4, 3),
            ("REHASH_END",), ("SEARCH", 8, 3), ("REMOVE", 4, 3),
            ("REMOVE", 8, 3),
        ])
        self.assertEqual(pasos[2].tabla, [[8, 4], []])
        self.assertEqual(pasos[3].tabla, [[], [], [], [4, 8]])
        self.assertEqual(pasos[4].tabla, pasos[3].tabla)
        self.assertEqual(pasos[5].tabla[3], [8])
        self.assertEqual(pasos[6].tabla[3], [])

    def test_rehash_incompleto_y_registro_mezclado(self):
        with self.assertRaisesRegex(ValueError, "rehash no reubicó"):
            preparar_pasos([("INSERT", 2, 2), ("REHASH", 5, 10), ("REHASH_END",)])
        with self.assertRaisesRegex(ValueError, "Rehash incompleto"):
            preparar_pasos([("REHASH", 5, 10), ("INSERT", 19, 9)])
        with self.assertRaisesRegex(ValueError, "mezcla tablas"):
            preparar_pasos([("INSERT", 2, 2), ("INSERT", 2, 1)])

    def test_init_separa_tablas_y_actualizar_no_duplica(self):
        pasos = preparar_pasos([
            ("INIT", 5), ("INSERT", 2, 2), ("INSERT", 2, 2),
            ("INIT", 3), ("INSERT", 2, 1),
        ])
        self.assertEqual(pasos[2].tabla[2], [2])
        self.assertEqual(pasos[-1].tabla, [[], [2], []])

    def test_geometria_sin_solapamientos(self):
        with tempfile.TemporaryDirectory() as carpeta, tempconfig({"media_dir": carpeta}):
            for capacidad in (5, 10, 20):
                tabla = [[] for _ in range(capacidad)]
                tabla[0] = list(range(12))
                tabla[-1] = [123456]
                buckets, nodos, enlaces = crear_tabla(tabla)
                objetos = list(buckets.values()) + list(nodos.values())
                grupo = VGroup(*objetos, enlaces)
                self.assertGreater(grupo.get_bottom()[1], -config.frame_height / 2 + 0.7)
                self.assertLess(grupo.get_top()[1], config.frame_height / 2 - 1.6)
                self.assertLess(grupo.width, config.frame_width)
                self.assertEqual(len(enlaces), len(nodos))
                for i, a in enumerate(objetos):
                    for b in objetos[i + 1:]:
                        overlap_x = min(a.get_right()[0], b.get_right()[0]) - max(a.get_left()[0], b.get_left()[0])
                        overlap_y = min(a.get_top()[1], b.get_top()[1]) - max(a.get_bottom()[1], b.get_bottom()[1])
                        self.assertFalse(overlap_x > 0 and overlap_y > 0)


if __name__ == "__main__":
    unittest.main()
