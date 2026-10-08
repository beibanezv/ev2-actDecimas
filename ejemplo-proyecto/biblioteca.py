"""Biblioteca personal: registro, préstamo y devolución de libros."""

import json
from pathlib import Path

RUTA_DATOS = Path(__file__).parent / "biblioteca.json"


class Biblioteca:
    def __init__(self, ruta: Path = RUTA_DATOS) -> None:
        self.ruta = ruta
        self.libros: list[dict] = []
        if self.ruta.exists():
            self.libros = json.loads(self.ruta.read_text(encoding="utf-8"))

    def _guardar(self) -> None:
        self.ruta.write_text(json.dumps(self.libros, ensure_ascii=False, indent=2), encoding="utf-8")

    def agregar(self, titulo: str, autor: str) -> dict:
        libro = {"id": len(self.libros) + 1, "titulo": titulo, "autor": autor, "prestado_a": None}
        self.libros.append(libro)
        self._guardar()
        return libro

    def prestar(self, libro_id: int, persona: str) -> bool:
        libro = self._buscar(libro_id)
        if libro is None or libro["prestado_a"] is not None:
            return False
        libro["prestado_a"] = persona
        self._guardar()
        return True

    def devolver(self, libro_id: int) -> bool:
        libro = self._buscar(libro_id)
        if libro is None or libro["prestado_a"] is None:
            return False
        libro["prestado_a"] = None
        self._guardar()
        return True

    def _buscar(self, libro_id: int) -> dict | None:
        for libro in self.libros:
            if libro["id"] == libro_id:
                return libro
        return None


if __name__ == "__main__":
    import sys

    bib = Biblioteca()
    args = sys.argv[1:]
    if not args:
        print("uso: biblioteca.py {agregar|prestar|devolver|listar} ...")
    elif args[0] == "agregar" and len(args) == 3:
        print(bib.agregar(args[1], args[2]))
    elif args[0] == "prestar" and len(args) == 3:
        print("prestado" if bib.prestar(int(args[1]), args[2]) else "no se pudo prestar")
    elif args[0] == "devolver" and len(args) == 2:
        print("devuelto" if bib.devolver(int(args[1])) else "no se pudo devolver")
    elif args[0] == "listar":
        for libro in bib.libros:
            estado = f"prestado a {libro['prestado_a']}" if libro["prestado_a"] else "disponible"
            print(f"[{libro['id']}] {libro['titulo']} — {libro['autor']} ({estado})")
