"""Agentes del escenario.

``Estudiante`` une los dos mundos de los archivos base:

* coordinación (``AgenteCoordinado``, de ``9-multi-agent-coordination.py``):
  capacidades, conocimiento y mensajes;
* recursos (``AgenteRecurso``, de ``10-conflict-resolution.py``):
  prioridad, recursos solicitados y deadline.

La política de cada agente es **determinista** (roles fijos), para que una
misma semilla reproduzca siempre la misma corrida: el LLM solo media y redacta,
no decide (error #1 de la guía).
"""

from __future__ import annotations

from .coordinacion import AgenteCoordinado
from .conflictos import AgenteRecurso

ROLES = ("coordinador", "investigador", "analista", "redactor")


class Estudiante(AgenteCoordinado, AgenteRecurso):
    def __init__(self, id: str, nombre: str, rol: str, capacidades,
                 prioridad: int = 2, semana_limite: int = 6,
                 afinidad_temas=(), preferencias_seccion=()) -> None:
        AgenteCoordinado.__init__(self, id, nombre, capacidades)
        AgenteRecurso.__init__(self, id, nombre, prioridad)
        if rol not in ROLES:
            raise ValueError(f"rol desconocido: {rol}")
        self.rol = rol
        self.semana_limite = semana_limite
        self.afinidad_temas = list(afinidad_temas)   # índices de temas, en orden de preferencia
        self.preferencias_seccion = list(preferencias_seccion)
        self.seccion_asignada: str | None = None

    # --- políticas deterministas -------------------------------------------
    def votar(self, opciones: list[str]) -> str:
        for i in self.afinidad_temas:
            if 0 <= i < len(opciones):
                return opciones[i]
        return opciones[0]

    def elegir_seccion(self, opciones: list[str]) -> str | None:
        for sec in self.preferencias_seccion:
            if sec in opciones:
                return sec
        return None

    def politica_propuesta(self, propuesta: str) -> bool:
        # Acepta solo lo que está entre sus secciones preferidas (criterio real,
        # a diferencia del auto-accept del archivo base).
        return propuesta in self.preferencias_seccion

    def __repr__(self) -> str:  # pragma: no cover - solo para depurar
        return f"<Estudiante {self.id} ({self.rol})>"
