"""Pruebas de integración: el escenario corre completo y es reproducible."""

from simulacion.conflictos import EstrategiaResolucion
from simulacion.escenario import ejecutar


def test_escenario_completo_determinista():
    r = ejecutar(EstrategiaResolucion.ARBITRAJE, semilla=42, mediador=None)
    d, m = r["decisiones"], r["metricas"]
    assert d["tema"]
    assert d["secciones"] and all(v for v in d["secciones"].values())
    assert m["mensajes"] > 0
    assert m["conflictos_detectados"] >= 3  # prioridad + recursos + temporal
    assert m["conflictos_resueltos"] == m["conflictos_detectados"]
    assert m["tokens_mediador_salida"] == 0  # sin mediador
    assert "Acta" in r["acta"] or "acta" in r["acta"].lower()


def test_misma_semilla_produce_la_misma_decision():
    a = ejecutar(EstrategiaResolucion.VOTACION, 42, None)["decisiones"]
    b = ejecutar(EstrategiaResolucion.VOTACION, 42, None)["decisiones"]
    assert a == b


def test_estrategias_distintas_pueden_asignar_recursos_distintos():
    resultados = {e: ejecutar(e, 42, None)["metricas"]["asignaciones"]
                  for e in (EstrategiaResolucion.PRIORIDAD, EstrategiaResolucion.COMPROMISO)}
    # el compromiso reparte 'sala_de_trabajo' en lugar de asignarla a un ganador único
    assert resultados[EstrategiaResolucion.PRIORIDAD]["sala_de_trabajo"] == "Analista"
    assert resultados[EstrategiaResolucion.COMPROMISO]["sala_de_trabajo"] == "compartido"
