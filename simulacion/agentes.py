"""Miembros del equipo que produce el entregable.

``MiembroEquipo`` une los dos mundos de los archivos base:

* coordinación (``AgenteCoordinado``, de ``9-multi-agent-coordination.py``):
  capacidades, conocimiento compartido y mensajes;
* recursos (``AgenteRecurso``, de ``10-conflict-resolution.py``):
  prioridad, recursos solicitados y deadline.

Roles del equipo (coherentes con la idea original del proyecto):

* **coordinador** — recibe la solicitud, divide el informe en secciones y las
  asigna por capacidad;
* **analista**    — lee el proyecto objetivo (README/agents.md/árbol) y
  extrae el brief de hechos;
* **redactor**    — escribe el informe usando *solo* el brief (anti-alucinación);
* **revisor**     — revisa cada borrador contra una checklist objetiva y emite
  veredicto estructurado (aprobado / rechazado + motivos + correcciones).

Las políticas de cada miembro son deterministas: quién gana cada conflicto lo
decide el protocolo, no el LLM (error #1 de la guía).
"""

from __future__ import annotations

from .coordinacion import AgenteCoordinado
from .conflictos import AgenteRecurso

ROLES = ("coordinador", "analista", "redactor", "revisor")


class MiembroEquipo(AgenteCoordinado, AgenteRecurso):
    def __init__(self, id: str, nombre: str, rol: str, capacidades,
                 prioridad: int = 3, semana_limite: int = 6,
                 postulaciones=()) -> None:
        AgenteCoordinado.__init__(self, id, nombre, capacidades)
        AgenteRecurso.__init__(self, id, nombre, prioridad)
        if rol not in ROLES:
            raise ValueError(f"rol desconocido: {rol}")
        self.rol = rol
        self.semana_limite = semana_limite
        self.postulaciones = list(postulaciones)  # secciones que quiere escribir, en orden
        self.seccion_asignada: str | None = None

    # --- políticas deterministas -------------------------------------------
    def postular(self, opciones: list[str]) -> list[str]:
        """Secciones a las que se postula este miembro (para el reparto)."""
        return [s for s in self.postulaciones if s in opciones]

    def politica_propuesta(self, propuesta: str) -> bool:
        # Acepta una sección solo si se postuló a ella (criterio real de capacidad,
        # a diferencia del auto-accept del archivo base).
        return propuesta in self.postulaciones

    def votar(self, opciones: list[str]) -> str:
        # Usado por votacion_multiple si el conflicto se somete al equipo.
        preferencia = {
            "revisor": "aplicar_correcciones",
            "redactor": "aceptar_borrador",
            "analista": "aplicar_correcciones",
            "coordinador": "aceptar_borrador",
        }.get(self.rol, opciones[0])
        return preferencia if preferencia in opciones else opciones[0]

    def __repr__(self) -> str:  # pragma: no cover - solo para depurar
        return f"<MiembroEquipo {self.id} ({self.rol})>"
