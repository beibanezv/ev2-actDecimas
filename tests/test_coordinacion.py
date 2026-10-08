"""Pruebas de la capa de coordinación (adaptación de 9-multi-agent-coordination.py)."""

from simulacion.coordinacion import AgenteCoordinado, Coordinador, TipoMensaje


class AgenteVotante(AgenteCoordinado):
    """Agente con voto fijo, para probar la votación multi-opción."""

    def __init__(self, id, nombre, voto=None, capacidades=()):
        super().__init__(id, nombre, capacidades)
        self._voto = voto

    def votar(self, opciones):
        return self._voto if self._voto in opciones else opciones[0]


def test_broadcast_entrega_a_todos_los_agentes():
    coord = Coordinador()
    a, b = AgenteCoordinado("a", "A", ()), AgenteCoordinado("b", "B", ())
    coord.registrar_agente(a)
    coord.registrar_agente(b)
    coord.broadcast(TipoMensaje.INFORMACION, "hola equipo")
    coord.procesar_todos()
    assert len(coord.registro_mensajes) == 2
    assert a.bandeja == [] and b.bandeja == []  # todos procesaron su bandeja


def test_votacion_multiple_gana_la_mayoria():
    coord = Coordinador()
    coord.registrar_agente(AgenteVotante("a", "A", voto="t1"))
    coord.registrar_agente(AgenteVotante("b", "B", voto="t1"))
    coord.registrar_agente(AgenteVotante("c", "C", voto="t2"))
    r = coord.votacion_multiple("¿Tema?", ["t1", "t2"])
    assert r["conteo"] == {"t1": 2, "t2": 1}
    assert r["ganador"] == "t1"
    assert not r["empate"]


def test_votacion_multiple_detecta_empate():
    coord = Coordinador()
    coord.registrar_agente(AgenteVotante("a", "A", voto="t1"))
    coord.registrar_agente(AgenteVotante("b", "B", voto="t2"))
    r = coord.votacion_multiple("¿Tema?", ["t1", "t2"])
    assert r["empate"] is True
    assert r["ganador"] is None
    assert sorted(r["empatados"]) == ["t1", "t2"]


def test_asignacion_por_capacidad_encuentra_al_agente():
    coord = Coordinador()
    coord.registrar_agente(AgenteCoordinado("red", "Redactor", ("redaccion",)))
    coord.registrar_agente(AgenteCoordinado("ana", "Analista", ("estadistica",)))
    elegido = coord.asignar_por_capacidad("estadistica")
    assert elegido is not None and elegido.id == "ana"
