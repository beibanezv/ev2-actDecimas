"""Pruebas del equipo LLM: sin clave cae a los redactores deterministas."""

from simulacion.mediador_llm import (
    MediadorLLM,
    _parse_json,
    analizar_determinista,
    laudo_determinista,
    redactar_determinista,
    revisar_determinista,
)

from simulacion.escenario import RAIZ_EJEMPLO, leer_proyecto

SECCIONES = ("Resumen ejecutivo", "Arquitectura", "Estado y pruebas", "Riesgos y pendientes")


def test_sin_clave_el_equipo_cae_a_determinista(monkeypatch):
    monkeypatch.setattr("simulacion.mediador_llm._cargar_entorno", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    m = MediadorLLM(activo=True)
    assert not m.disponible
    assert m.fallback_usado
    texto = m.proponer(type("C", (), {
        "id": 1, "tipo": type("T", (), {"value": "objetivo"})(),
        "recurso": "informe_v1"})(), [], 1, "el revisor aplica correcciones", 3)
    assert "determinista" in texto


def test_mediador_desactivado_no_llama_al_llm():
    m = MediadorLLM(activo=False)
    assert not m.disponible and m.llamadas == 0


def test_parse_json_tolera_bloques_y_texto_extra():
    assert _parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert _parse_json('Claro: {"a": 2} listo.') == {"a": 2}
    assert _parse_json("sin json") is None


def test_redactar_determinista_incluye_las_4_secciones():
    informe = redactar_determinista({"proyecto": "X", "componentes": ["a"], "huecos": []})
    for sec in SECCIONES:
        assert f"## {sec}" in informe


def test_analizar_determinista_cita_los_archivos_leidos():
    material = leer_proyecto(RAIZ_EJEMPLO)
    brief = analizar_determinista(material)
    assert brief["proyecto"] == "ejemplo-proyecto"
    assert "README.md" in brief["archivos_citados"]
    assert brief["stack"] and brief["metricas"]


def test_revisar_determinista_deriva_los_motivos_de_la_checklist():
    veredicto = revisar_determinista(
        {"aprobado": False, "fallos": [{"seccion": "Arquitectura",
                                        "descripcion": "falta la sección",
                                        "solucion": "añádela"}]})
    assert not veredicto["aprobado"]
    assert veredicto["motivos"] == ["falta la sección"]
    assert veredicto["correcciones"][0]["solucion"] == "añádela"


def test_laudo_determinista_menciona_las_rondas_agotadas():
    laudo = laudo_determinista([{"ronda": 1, "motivos": ["muy corto"]},
                                {"ronda": 2, "motivos": ["sigue corto"]}])
    assert "2 rondas" in laudo and "muy corto" not in laudo
