"""Pruebas del mediador LLM: sin clave cae al redactor determinista."""

from simulacion.mediador_llm import MediadorLLM, acta_determinista


class ConflictoFalso:
    id = 1
    tipo = type("T", (), {"value": "recurso"})()
    recurso = "acceso_base_datos"


class AgenteFalso:
    nombre = "Investigador"
    prioridad = 1
    semana_limite = 3


def test_sin_clave_el_mediador_cae_a_determinista(monkeypatch):
    monkeypatch.setattr("simulacion.mediador_llm._cargar_entorno", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    m = MediadorLLM(activo=True)
    assert not m.disponible
    assert m.fallback_usado
    texto = m.proponer(ConflictoFalso(), [AgenteFalso()], 1,
                       "el de mayor prioridad conserva el acceso", 3)
    assert "determinista" in texto


def test_mediador_desactivado_no_llama_al_llm(monkeypatch):
    m = MediadorLLM(activo=False)
    assert not m.disponible
    assert m.llamadas == 0


def test_acta_determinista_incluye_las_decisiones():
    acta = acta_determinista({
        "tema": "Tema de prueba",
        "secciones": {"Análisis": ["Analista"]},
        "recursos_asignados": {"Analista": ["software"]},
        "conflictos": [{"id": 1, "tipo": "recurso", "recurso": "x",
                        "resolucion": "lo gana el Analista"}],
    })
    assert "Tema de prueba" in acta
    assert "Analista" in acta
    assert "lo gana el Analista" in acta
