"""Pruebas del CLI: scaffold de --tema y modo --breve de la consola."""

from __future__ import annotations

import main
from simulacion.bitacora import Bitacora


def test_preparar_material_tema_crea_dos_notas(tmp_path):
    carpeta = main.preparar_material_tema("Etica en IA", tmp_path)
    assert carpeta.name == "tema-etica-en-ia"
    mds = list(carpeta.glob("*.md"))
    assert len(mds) == 2
    contenidos = " ".join(p.read_text(encoding="utf-8") for p in mds)
    assert "Etica en IA" in contenidos


def test_preparar_material_tema_es_idempotente(tmp_path):
    main.preparar_material_tema("Etica en IA", tmp_path)
    notas = tmp_path / "tema-etica-en-ia" / "notas.md"
    notas.write_text("mis notas editadas a mano", encoding="utf-8")
    main.preparar_material_tema("Etica en IA", tmp_path)  # no debe pisar
    assert notas.read_text(encoding="utf-8") == "mis notas editadas a mano"


def test_modo_breve_filtra_consola_pero_guarda_todo(capsys):
    lineas = ["  mensaje interno de coordinacion", "[Fase 2] algo pasa"]
    completo = Bitacora()
    for l in lineas:
        completo.log(l)
    salida_completa = capsys.readouterr().out
    assert "mensaje interno de coordinacion" in salida_completa

    breve = Bitacora()
    breve.breve = True
    for l in lineas:
        breve.log(l)
    salida_breve = capsys.readouterr().out
    assert "mensaje interno de coordinacion" not in salida_breve
    assert "[Fase 2]" in salida_breve
    # el registro interno conserva todo (es lo que se escribe en evidencia/)
    assert "mensaje interno de coordinacion" in breve.volcado()
