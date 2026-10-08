"""Pruebas del dominio de Biblioteca (python test_biblioteca.py)."""

import tempfile
import unittest
from pathlib import Path

from biblioteca import Biblioteca


class TestBiblioteca(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp()) / "datos.json"
        self.bib = Biblioteca(self.tmp)

    def test_agregar_asigna_id_incremental(self) -> None:
        self.assertEqual(self.bib.agregar("Rayuela", "Cortázar")["id"], 1)
        self.assertEqual(self.bib.agregar("El túnel", "Sábato")["id"], 2)

    def test_prestar_falla_si_ya_esta_prestado(self) -> None:
        libro = self.bib.agregar("Rayuela", "Cortázar")
        self.assertTrue(self.bib.prestar(libro["id"], "Ana"))
        self.assertFalse(self.bib.prestar(libro["id"], "Beto"))

    def test_devolver_libera_el_libro(self) -> None:
        libro = self.bib.agregar("Rayuela", "Cortázar")
        self.bib.prestar(libro["id"], "Ana")
        self.assertTrue(self.bib.devolver(libro["id"]))
        self.assertIsNone(self.bib.libros[0]["prestado_a"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
