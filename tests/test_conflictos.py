"""Pruebas de la capa de conflictos (adaptación de 10-conflict-resolution.py)."""

import random

from simulacion.conflictos import (
    AgenteRecurso,
    EstrategiaResolucion,
    ResolvedorConflictos,
)


def equipo():
    r = ResolvedorConflictos(rng=random.Random(42))
    inv = AgenteRecurso("inv", "Investigador", prioridad=2)
    ana = AgenteRecurso("ana", "Analista", prioridad=1)
    red = AgenteRecurso("red", "Redactor", prioridad=3)
    for a in (inv, ana, red):
        r.registrar_agente(a)
    r.agregar_recurso("acceso_base_datos")
    return r, inv, ana, red


def conflicto_de_recurso(r, inv, ana):
    inv.solicitar_recurso("acceso_base_datos")
    ana.solicitar_recurso("acceso_base_datos")
    detectados = r.detectar_conflicto_recurso()
    assert len(detectados) == 1
    return detectados[0]


def test_detecta_conflicto_solo_con_mas_de_un_solicitante():
    r, inv, ana, red = equipo()
    inv.solicitar_recurso("acceso_base_datos")  # un solo solicitante
    assert r.detectar_conflicto_recurso() == []


def test_estrategia_prioridad_gana_el_de_menor_numero():
    r, inv, ana, red = equipo()
    c = conflicto_de_recurso(r, inv, ana)
    r.resolver(c, EstrategiaResolucion.PRIORIDAD)
    assert c.asignado_a == "ana" and c.resuelto and ana.tiene_recurso("acceso_base_datos")


def test_estrategia_primero_en_llegar_gana_el_que_pidio_antes():
    r, inv, ana, red = equipo()
    c = conflicto_de_recurso(r, inv, ana)
    r.resolver(c, EstrategiaResolucion.PRIMERO_EN_LLEGADA)
    # inv se registró antes que ana
    assert c.asignado_a == "inv"


def test_estrategia_compromiso_reparte_el_acceso():
    r, inv, ana, red = equipo()
    c = conflicto_de_recurso(r, inv, ana)
    r.resolver(c, EstrategiaResolucion.COMPROMISO)
    assert c.resuelto and c.asignado_a == "" and "50" in c.resolucion


def test_estrategia_votacion_es_reproducible_con_la_misma_semilla():
    r1, i1, a1, _ = equipo()
    c1 = conflicto_de_recurso(r1, i1, a1)
    r1.resolver(c1, EstrategiaResolucion.VOTACION)
    r2, i2, a2, _ = equipo()
    c2 = conflicto_de_recurso(r2, i2, a2)
    r2.resolver(c2, EstrategiaResolucion.VOTACION)
    assert c1.asignado_a == c2.asignado_a


def test_estrategia_arbitraje_usa_el_deadline():
    r, inv, ana, red = equipo()
    r.agregar_slot("revision", 1)
    inv.solicitar_recurso("revision")
    ana.solicitar_recurso("revision")
    inv.semana_limite, ana.semana_limite = 3, 5
    (c,) = r.detectar_conflicto_temporal()
    r.resolver(c, EstrategiaResolucion.ARBITRAJE)
    assert c.tipo.value == "temporal"
    assert c.asignado_a == "inv"  # deadline semana 3 es más próximo que semana 5


def test_negociacion_agota_el_tope_de_3_rondas_con_mediador():
    class MediadorFalso:
        def __init__(self):
            self.llamadas = 0

        def proponer(self, conflicto, agentes, ronda, terminos, max_rondas):
            self.llamadas += 1
            return f"propuesta de la ronda {ronda}"

    r, inv, ana, red = equipo()
    c = conflicto_de_recurso(r, inv, ana)
    inv.semana_limite, ana.semana_limite = 1, 4  # urgencia asimétrica
    mediador = MediadorFalso()
    r.resolver(c, EstrategiaResolucion.NEGOCIACION, mediador=mediador)
    assert c.rondas == 3 and mediador.llamadas == 3 and c.resuelto


def test_negociacion_acuerda_en_ronda_1_con_urgencia_simetrica():
    r, inv, ana, red = equipo()
    c = conflicto_de_recurso(r, inv, ana)
    inv.semana_limite = ana.semana_limite = 4
    r.resolver(c, EstrategiaResolucion.NEGOCIACION)
    assert c.rondas == 1 and c.asignado_a == "ana"  # acuerdo por prioridad en ronda 1
