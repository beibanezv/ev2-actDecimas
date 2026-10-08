"""Resolución de conflictos — adaptación de
``Ingenieria-de-Soluciones-con-IA/RA2/IL2.3/10-conflict-resolution.py``.

Mapeo de nombres (base → aquí)::

    ConflictType → TipoConflicto          ResolutionStrategy → EstrategiaResolucion
    Conflict → Conflicto                  Agent → AgenteRecurso
    ConflictResolver → ResolvedorConflictos
    detect_resource_conflict → detectar_conflicto_recurso
    resolve_conflict → resolver

Tres extensiones sobre el archivo base:

1. El base declara ``ARBITRATION`` y ``FIRST_COME`` en el enum pero **no los
   implementa**; aquí ``resolver_por_arbitraje`` y ``resolver_primero_en_llegada``
   sí funcionan, con criterio explícito y trazable.
2. ``resolver_por_votacion`` recibe un ``rng`` (``random.Random`` con semilla):
   el base usaba ``random`` global, así que sus corridas no eran reproducibles.
3. La negociación tiene **tope duro de rondas** (``MAX_RONDAS_NEGOCIACION``);
   al agotarse, el árbitro decide. El mediador LLM solo *redacta* las
   propuestas: quién gana cada ronda lo fija el protocolo determinista.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from .bitacora import BITACORA

# Error #6 de la guía: tope duro de iteraciones.
MAX_RONDAS_NEGOCIACION = 3


class TipoConflicto(Enum):
    RECURSO = "recurso"
    OBJETIVO = "objetivo"
    PRIORIDAD = "prioridad"
    TEMPORAL = "temporal"


class EstrategiaResolucion(Enum):
    PRIORIDAD = "prioridad"
    NEGOCIACION = "negociacion"
    ARBITRAJE = "arbitraje"
    VOTACION = "votacion"
    COMPROMISO = "compromiso"
    PRIMERO_EN_LLEGADA = "primero_en_llegada"


@dataclass
class Conflicto:
    id: int
    tipo: TipoConflicto
    agentes_involucrados: list
    recurso: str
    descripcion: str
    severidad: int = 1
    resuelto: bool = False
    resolucion: str = ""
    rondas: int = 0
    estrategia: str = ""
    asignado_a: str = ""  # id del agente ganador (vacío si el acceso es compartido)


class AgenteRecurso:
    """Agente con prioridad y recursos (base: ``Agent`` de 10-conflict-resolution.py)."""

    def __init__(self, id: str, nombre: str, prioridad: int = 1) -> None:
        self.id = id
        self.nombre = nombre
        self.prioridad = prioridad
        self.recursos: list[str] = []
        self.recursos_solicitados: list[str] = []
        self.orden_llegada = 0
        self.semana_limite = 1  # deadline del agente (para conflictos temporales)

    def solicitar_recurso(self, rid: str) -> "AgenteRecurso":
        if rid not in self.recursos_solicitados:
            self.recursos_solicitados.append(rid)
        return self

    def tiene_recurso(self, rid: str) -> bool:
        return rid in self.recursos

    def dar_recurso(self, rid: str, otro: "AgenteRecurso") -> bool:
        if rid in self.recursos:
            self.recursos.remove(rid)
            otro.recursos.append(rid)
            return True
        return False

    def otorgar(self, rid: str) -> None:
        if rid not in self.recursos:
            self.recursos.append(rid)
        if rid in self.recursos_solicitados:
            self.recursos_solicitados.remove(rid)


class ResolvedorConflictos:
    """Detecta y resuelve conflictos de recursos, prioridad y tiempo."""

    def __init__(self, nombre: str = "Resolvedor de conflictos", rng: random.Random | None = None) -> None:
        self.nombre = nombre
        self.agentes: dict[str, AgenteRecurso] = {}
        self.conflictos: list[Conflicto] = []
        self.recursos: set[str] = set()
        self.slots: dict[str, int] = {}
        self.rng = rng or random.Random()
        self._contador = 0
        self._orden = 0

    # --- registro ----------------------------------------------------------
    def registrar_agente(self, agente: AgenteRecurso) -> "ResolvedorConflictos":
        self.agentes[agente.id] = agente
        agente.orden_llegada = self._orden
        self._orden += 1
        return self

    def agregar_recurso(self, rid: str) -> "ResolvedorConflictos":
        self.recursos.add(rid)
        return self

    def agregar_slot(self, sid: str, capacidad: int = 1) -> "ResolvedorConflictos":
        self.slots[sid] = capacidad
        return self

    # --- detección ---------------------------------------------------------
    def nuevo_conflicto(self, tipo: TipoConflicto, agentes, recurso: str,
                        descripcion: str, severidad: int) -> Conflicto:
        """Crea y registra un conflicto (usado por el escenario, p. ej. empates)."""
        return self._nuevo_conflicto(tipo, agentes, recurso, descripcion, severidad)

    def _nuevo_conflicto(self, tipo: TipoConflicto, agentes, recurso: str,
                         descripcion: str, severidad: int) -> Conflicto:
        self._contador += 1
        conflicto = Conflicto(self._contador, tipo, list(agentes), recurso, descripcion, severidad)
        self.conflictos.append(conflicto)
        return conflicto

    def detectar_conflicto_recurso(self) -> list[Conflicto]:
        """Conflicto RECURSO: más de un agente pide el mismo recurso exclusivo."""
        solicitantes: dict[str, list[AgenteRecurso]] = {}
        for a in self.agentes.values():
            for r in a.recursos_solicitados:
                if r in self.slots:
                    continue  # los slots se detectan como conflicto temporal
                solicitantes.setdefault(r, []).append(a)
        nuevos = []
        for r, agentes in solicitantes.items():
            if len(agentes) > 1:
                nombres = ", ".join(a.nombre for a in agentes)
                nuevos.append(self._nuevo_conflicto(
                    TipoConflicto.RECURSO, agentes, r,
                    f"{len(agentes)} agentes solicitan el recurso exclusivo '{r}': {nombres}", 3))
        return nuevos

    def detectar_conflicto_temporal(self) -> list[Conflicto]:
        """Conflicto TEMPORAL: más agentes que capacidad piden el mismo slot."""
        solicitantes: dict[str, list[AgenteRecurso]] = {}
        for a in self.agentes.values():
            for r in a.recursos_solicitados:
                if r in self.slots:
                    solicitantes.setdefault(r, []).append(a)
        nuevos = []
        for slot, agentes in solicitantes.items():
            if len(agentes) > self.slots.get(slot, 1):
                detalle = ", ".join(f"{a.nombre} (deadline semana {a.semana_limite})" for a in agentes)
                nuevos.append(self._nuevo_conflicto(
                    TipoConflicto.TEMPORAL, agentes, slot,
                    f"{len(agentes)} agentes compiten por el slot '{slot}' "
                    f"(capacidad {self.slots[slot]}): {detalle}", 2))
        return nuevos

    def detectar_conflicto_prioridad(self, seccion: str, aspirantes) -> Conflicto | None:
        """Conflicto PRIORIDAD: dos agentes quieren la misma subtarea."""
        if len(aspirantes) <= 1:
            return None
        nombres = ", ".join(a.nombre for a in aspirantes)
        return self._nuevo_conflicto(
            TipoConflicto.PRIORIDAD, aspirantes, seccion,
            f"{len(aspirantes)} agentes quieren la misma subtarea '{seccion}': {nombres}", 2)

    # --- estrategias -------------------------------------------------------
    def resolver_por_prioridad(self, c: Conflicto) -> Conflicto:
        ganador = min(c.agentes_involucrados, key=lambda a: (a.prioridad, a.orden_llegada))
        for a in c.agentes_involucrados:
            if a is not ganador and c.recurso in a.recursos_solicitados:
                a.recursos_solicitados.remove(c.recurso)
        ganador.otorgar(c.recurso)
        c.asignado_a = ganador.id
        c.resolucion = (f"Por prioridad: {ganador.nombre} (prioridad {ganador.prioridad}) "
                        f"obtiene '{c.recurso}'.")
        c.resuelto = True
        return c

    def resolver_primero_en_llegar(self, c: Conflicto) -> Conflicto:
        ganador = min(c.agentes_involucrados, key=lambda a: a.orden_llegada)
        for a in c.agentes_involucrados:
            if a is not ganador and c.recurso in a.recursos_solicitados:
                a.recursos_solicitados.remove(c.recurso)
        ganador.otorgar(c.recurso)
        c.asignado_a = ganador.id
        c.resolucion = (f"Primero en llegar: {ganador.nombre} solicitó '{c.recurso}' "
                        f"antes (orden {ganador.orden_llegada}) y se lo queda.")
        c.resuelto = True
        return c

    def resolver_por_votacion(self, c: Conflicto) -> Conflicto:
        agentes = c.agentes_involucrados
        votos = {a.id: self.rng.choice(agentes) for a in agentes}
        conteo: dict[str, int] = {}
        for v in votos.values():
            conteo[v.id] = conteo.get(v.id, 0) + 1

        def desempate(par):
            # a igualdad de votos gana el de menor orden de llegada (determinista)
            return (par[1], -self.agentes[par[0]].orden_llegada)

        ganador_id = max(conteo.items(), key=desempate)[0]
        ganador = self.agentes[ganador_id]
        for a in agentes:
            if a is not ganador and c.recurso in a.recursos_solicitados:
                a.recursos_solicitados.remove(c.recurso)
        ganador.otorgar(c.recurso)
        c.asignado_a = ganador.id
        detalle = ", ".join(f"{self.agentes[k].nombre}: {n}" for k, n in conteo.items())
        c.resolucion = f"Por votación ({detalle}) gana {ganador.nombre} para '{c.recurso}'."
        c.resuelto = True
        return c

    def resolver_por_compromiso(self, c: Conflicto) -> Conflicto:
        n = len(c.agentes_involucrados)
        partes = ", ".join(a.nombre for a in c.agentes_involucrados)
        c.asignado_a = ""
        c.resolucion = (f"Compromiso: '{c.recurso}' se divide en {n} partes iguales "
                        f"({100 // n}% cada una) entre {partes}.")
        c.resuelto = True
        return c

    def resolver_por_arbitraje(self, c: Conflicto, criterio: str | None = None) -> Conflicto:
        """Arbitraje con criterio EXPLÍCITO (no al azar): deadline o prioridad."""
        if c.tipo == TipoConflicto.TEMPORAL:
            ganador = min(c.agentes_involucrados, key=lambda a: (a.semana_limite, a.orden_llegada))
            criterio = criterio or "deadline más próximo va primero"
        else:
            ganador = min(c.agentes_involucrados, key=lambda a: (a.prioridad, a.orden_llegada))
            criterio = criterio or "prioridad y orden de llegada"
        for a in c.agentes_involucrados:
            if a is not ganador and c.recurso in a.recursos_solicitados:
                a.recursos_solicitados.remove(c.recurso)
        ganador.otorgar(c.recurso)
        c.asignado_a = ganador.id
        c.resolucion = (f"Arbitraje ({criterio}): {ganador.nombre} obtiene '{c.recurso}'.")
        c.resuelto = True
        return c

    def resolver_por_negociacion(self, c: Conflicto, mediador=None) -> Conflicto:
        """Negociación con tope duro de rondas.

        El protocolo fija los términos de cada ronda; el mediador LLM solo los
        redacta. El acuerdo depende de la urgencia relativa (spread de deadlines),
        de modo que el tope de 3 rondas se ejerce cuando la urgencia es asimétrica.
        """
        agentes = c.agentes_involucrados
        semanas = [a.semana_limite for a in agentes]
        spread = max(semanas) - min(semanas)
        terminos_por_ronda = {
            1: "el agente con mayor prioridad conserva el acceso y el otro acepta el segundo turno",
            2: "reparto 50/50 del acceso (o de la carga asociada al recurso)",
            3: "arbitraje forzado: gana el agente con el deadline más próximo",
        }
        for ronda in range(1, MAX_RONDAS_NEGOCIACION + 1):
            c.rondas = ronda
            terminos = terminos_por_ronda[ronda]
            if mediador is not None:
                propuesta = mediador.proponer(c, agentes, ronda, terminos, MAX_RONDAS_NEGOCIACION)
            else:
                propuesta = f"Ronda {ronda}/{MAX_RONDAS_NEGOCIACION} — mediador determinista: {terminos}"
            BITACORA.log(f"    [negociación] {propuesta}")
            if ronda == 1 and spread == 0:
                self.resolver_por_prioridad(c)
                c.resolucion += " (acuerdo en ronda 1: urgencia simétrica)"
                c.estrategia = "negociacion"
                return c
            if ronda == 2 and spread <= 1:
                self.resolver_por_compromiso(c)
                c.resolucion += " (acuerdo en ronda 2: urgencia levemente asimétrica)"
                c.estrategia = "negociacion"
                return c
        # ronda 3 alcanzada sin acuerdo → arbitraje forzado (tope duro)
        self.resolver_por_arbitraje(c, criterio="acuerdo forzado por tope de 3 rondas")
        c.estrategia = "negociacion"
        return c

    def resolver(self, c: Conflicto, estrategia: EstrategiaResolucion, mediador=None) -> Conflicto:
        if c.resuelto:
            return c
        rutas = {
            EstrategiaResolucion.PRIORIDAD: self.resolver_por_prioridad,
            EstrategiaResolucion.NEGOCIACION: self.resolver_por_negociacion,
            EstrategiaResolucion.ARBITRAJE: self.resolver_por_arbitraje,
            EstrategiaResolucion.VOTACION: self.resolver_por_votacion,
            EstrategiaResolucion.COMPROMISO: self.resolver_por_compromiso,
            EstrategiaResolucion.PRIMERO_EN_LLEGADA: self.resolver_primero_en_llegar,
        }
        if estrategia == EstrategiaResolucion.NEGOCIACION:
            self.resolver_por_negociacion(c, mediador=mediador)
        else:
            rutas[estrategia](c)
        if not c.estrategia:
            c.estrategia = estrategia.value
        BITACORA.log(f"  [conflicto #{c.id} · {c.tipo.value}] {c.resolucion}")
        return c

    def resolver_todos(self, estrategia: EstrategiaResolucion, mediador=None) -> list[Conflicto]:
        return [self.resolver(c, estrategia, mediador) for c in self.conflictos if not c.resuelto]

    # --- reporte -----------------------------------------------------------
    def generar_reporte(self) -> str:
        resueltos = sum(1 for c in self.conflictos if c.resuelto)
        lineas = ["REPORTE DE CONFLICTOS", f"Conflictos detectados: {len(self.conflictos)}",
                  f"Conflictos resueltos: {resueltos}/{len(self.conflictos)}"]
        for c in self.conflictos:
            estado = "RESUELTO" if c.resuelto else "PENDIENTE"
            lineas.append(f"  #{c.id} [{c.tipo.value}] sev {c.severidad}: {c.descripcion}")
            lineas.append(f"      → {estado} ({c.estrategia or 'sin estrategia'}, {c.rondas} ronda(s)): {c.resolucion or '-'}")
        return "\n".join(lineas)
