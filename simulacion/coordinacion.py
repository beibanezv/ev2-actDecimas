"""Coordinación multi-agente — adaptación de
``Ingenieria-de-Soluciones-con-IA/RA2/IL2.3/9-multi-agent-coordination.py``.

Mapeo de nombres (base → aquí)::

    MessageType → TipoMensaje          Message → Mensaje
    CoordinatedAgent → AgenteCoordinado  Coordinator → Coordinador
    send_message → enviar               share_knowledge → compartir_conocimiento
    voting_consensus → votacion_multiple

Dos extensiones sobre el archivo base:

1. ``Coordinador.votacion_multiple()``: el base solo votaba una propuesta
   sí/no; aquí se votan N opciones y se detecta el empate.
2. ``AgenteCoordinado._handle_propose``: el base auto-aceptaba cualquier
   propuesta; aquí aceptar o rechazar se delega en la política del agente
   (``politica_propuesta``), que en el escenario decide por capacidades.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .bitacora import BITACORA


class TipoMensaje(Enum):
    PETICION = "peticion"
    RESPUESTA = "respuesta"
    INFORMACION = "informacion"
    CONSULTA = "consulta"
    PROPUESTA = "propuesta"
    ACEPTACION = "aceptacion"
    RECHAZO = "rechazo"


@dataclass
class Mensaje:
    emisor: str
    receptor: str
    tipo: TipoMensaje
    contenido: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class AgenteCoordinado:
    """Agente con capacidades, conocimiento y bandeja (base: ``CoordinatedAgent``)."""

    def __init__(self, id: str, nombre: str, capacidades) -> None:
        self.id = id
        self.nombre = nombre
        self.capacidades = set(capacidades)
        self.conocimiento: dict[str, str] = {}
        self.bandeja: list[Mensaje] = []
        self.coordinador: "Coordinador" | None = None

    # --- comunicación -----------------------------------------------------
    def enviar(self, receptor: str, tipo: TipoMensaje, contenido: str):
        if self.coordinador is None:
            BITACORA.log(f"  [mail] {self.nombre} no está registrado; mensaje descartado")
            return None
        mensaje = Mensaje(self.id, receptor, tipo, contenido)
        return self.coordinador.entregar(mensaje)

    def recibir(self, mensaje: Mensaje) -> None:
        self.bandeja.append(mensaje)

    def procesar_mensajes(self) -> None:
        pendientes, self.bandeja = list(self.bandeja), []
        for m in pendientes:
            BITACORA.log(f"  [mail] {m.emisor} → {m.receptor} ({m.tipo.value}): {m.contenido}")
            self._despachar(m)

    def _despachar(self, m: Mensaje) -> None:
        rutas = {
            TipoMensaje.PETICION: self._handle_request,
            TipoMensaje.CONSULTA: self._handle_query,
            TipoMensaje.PROPUESTA: self._handle_propose,
            TipoMensaje.ACEPTACION: self._handle_accept,
            TipoMensaje.RECHAZO: self._handle_reject,
        }
        manejador = rutas.get(m.tipo)
        if manejador:
            manejador(m)

    # --- respuestas a mensajes -------------------------------------------
    def _handle_request(self, m: Mensaje) -> None:
        self.enviar(m.emisor, TipoMensaje.RESPUESTA, f"{self.nombre} recibió la petición")

    def _handle_query(self, m: Mensaje) -> None:
        self.enviar(m.emisor, TipoMensaje.RESPUESTA, self.conocimiento.get(m.contenido, "sin datos"))

    def _handle_propose(self, m: Mensaje) -> None:
        if self.politica_propuesta(m.contenido):
            self.enviar(m.emisor, TipoMensaje.ACEPTACION, f"{self.nombre} acepta: {m.contenido}")
        else:
            self.enviar(m.emisor, TipoMensaje.RECHAZO, f"{self.nombre} rechaza: {m.contenido}")

    def _handle_accept(self, m: Mensaje) -> None:
        BITACORA.log(f"    ✓ {self.nombre} anota la aceptación")

    def _handle_reject(self, m: Mensaje) -> None:
        BITACORA.log(f"    ✗ {self.nombre} anota el rechazo")

    # --- política (punto de extensión) ------------------------------------
    def politica_propuesta(self, propuesta: str) -> bool:
        """Por defecto se acepta; el escenario la sobreescribe con un criterio real."""
        return True

    def votar(self, opciones: list[str]) -> str:
        return opciones[0]

    def compartir_conocimiento(self, destinatarios, clave: str, valor: str) -> None:
        self.conocimiento[clave] = valor
        for d in destinatarios:
            self.enviar(d, TipoMensaje.INFORMACION, f"{clave}={valor}")


class Coordinador(AgenteCoordinado):
    """Coordina el equipo: reparte subtareas, envía mensajes y toma votaciones."""

    def __init__(self, nombre: str = "Coordinador del equipo", capacidades=("coordinacion",)) -> None:
        super().__init__("coord", nombre, capacidades)
        self.agentes: dict[str, AgenteCoordinado] = {}
        self.registro_mensajes: list[Mensaje] = []
        self.tareas: list[dict] = []

    def registrar_agente(self, agente: AgenteCoordinado) -> "Coordinador":
        agente.coordinador = self
        self.agentes[agente.id] = agente
        return self

    def entregar(self, mensaje: Mensaje):
        self.registro_mensajes.append(mensaje)
        destino = self.agentes.get(mensaje.receptor)
        if destino is None:
            return None
        destino.recibir(mensaje)
        return mensaje

    def broadcast(self, tipo: TipoMensaje, contenido: str, excluir=()) -> None:
        for aid in self.agentes:
            if aid not in excluir:
                self.entregar(Mensaje(self.id, aid, tipo, contenido))

    def anunciar_tarea(self, titulo: str, subtareas: list[str]) -> str:
        self.tareas.append({"titulo": titulo, "subtareas": subtareas})
        self.broadcast(TipoMensaje.PROPUESTA, f"Tarea '{titulo}' con {len(subtareas)} subtareas")
        return titulo

    def asignar_por_capacidad(self, capacidad: str):
        for a in self.agentes.values():
            if capacidad in a.capacidades:
                return a
        return None

    def procesar_todos(self) -> None:
        for a in self.agentes.values():
            a.procesar_mensajes()

    # --- votación multi-opción (extiende voting_consensus del base) --------
    def votacion_multiple(self, pregunta: str, opciones: list[str]) -> dict:
        votos = {a.id: a.votar(opciones) for a in self.agentes.values()}
        conteo = {o: 0 for o in opciones}
        for v in votos.values():
            conteo[v] += 1
        maximo = max(conteo.values())
        empatados = [o for o, n in conteo.items() if n == maximo]
        return {
            "pregunta": pregunta,
            "conteo": conteo,
            "votos": votos,
            "ganador": None if len(empatados) > 1 else empatados[0],
            "empate": len(empatados) > 1,
            "empatados": empatados,
        }

    def generar_reporte_comunicacion(self) -> str:
        tipos: dict[str, int] = {}
        for m in self.registro_mensajes:
            tipos[m.tipo.value] = tipos.get(m.tipo.value, 0) + 1
        lineas = ["REPORTE DE COMUNICACIÓN", f"Mensajes intercambiados: {len(self.registro_mensajes)}"]
        lineas += [f"  {t}: {n}" for t, n in sorted(tipos.items())]
        return "\n".join(lineas)
