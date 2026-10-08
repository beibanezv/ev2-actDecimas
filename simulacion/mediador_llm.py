"""Mediador LLM (ChatGroq) con rol acotado + redactor del acta.

Decisión de diseño (error #1 de la guía: *no usar LLM para todo*):
el protocolo multi-agente reparte secciones y resuelve conflictos en Python
puro; el LLM solo (a) redacta las propuestas de cada ronda de negociación y
(b) redacta el acta final. Tope: como máximo 3 llamadas de mediación por
conflicto más 1 acta por corrida. Sin clave o ante un 429, cae al redactor
determinista y la simulación sigue de pie (el reparto y los conflictos ya
están resueltos).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

MODELO_POR_DEFECTO = "openai/gpt-oss-20b"
RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"

SISTEMA_MEDIACION = (
    "Eres el mediador de un equipo académico de cuatro estudiantes que debe resolver "
    "un conflicto de coordinación. Redactas propuestas formales y breves (máximo 60 "
    "palabras), en español, sin inventar datos que no te entreguen."
)

SISTEMA_ACTA = (
    "Eres el secretario del equipo. Redactas el acta final de la sesión de coordinación "
    "en markdown, en español, con secciones: Tema aprobado, Equipo y secciones, Recursos "
    "asignados, Cronograma, Conflictos y resoluciones, Acuerdos. Máximo 300 palabras. "
    "No inventes datos que no estén en el JSON entregado."
)


def _cargar_entorno() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=RUTA_ENV)
    except Exception:
        pass


class MediadorLLM:
    def __init__(self, modelo: str = MODELO_POR_DEFECTO, temperatura: float = 0.3,
                 activo: bool = True) -> None:
        self.modelo = modelo
        self.activo = activo
        self._llm = None
        self._msg_sistema = None
        self._msg_humano = None
        self.llamadas = 0
        self.tokens_entrada = 0
        self.tokens_salida = 0
        self.tokens_estimados = False  # True si hubo que estimar por falta de usage
        self.fallback_usado = False
        self.motivo_fallback = ""
        _cargar_entorno()
        if not activo:
            self.motivo_fallback = "desactivado por configuración (--llm no)"
            return
        if not os.getenv("GROQ_API_KEY"):
            self.fallback_usado = True
            self.motivo_fallback = "GROQ_API_KEY ausente en el entorno"
            return
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_groq import ChatGroq

            self._llm = ChatGroq(model=modelo, temperature=temperatura, reasoning_effort="low")
            self._msg_sistema, self._msg_humano = SystemMessage, HumanMessage
        except Exception as e:  # sin red o dependencias incompletas
            self.fallback_usado = True
            self.motivo_fallback = f"{type(e).__name__}: {e}"

    @property
    def disponible(self) -> bool:
        return self._llm is not None

    @property
    def modo(self) -> str:
        if self.disponible:
            return f"LLM {self.modelo}"
        return f"determinista ({self.motivo_fallback})"

    @staticmethod
    def _extraer_tokens(respuesta) -> tuple[int, int]:
        """Tokens de la respuesta: usage_metadata o response_metadata de Groq."""
        um = getattr(respuesta, "usage_metadata", None) or {}
        e, s = um.get("input_tokens"), um.get("output_tokens")
        if not e and not s:
            md = getattr(respuesta, "response_metadata", None) or {}
            tu = md.get("token_usage") or {}
            e, s = tu.get("prompt_tokens"), tu.get("completion_tokens")
        return int(e or 0), int(s or 0)

    def _invocar(self, sistema: str, usuario: str) -> str | None:
        self.llamadas += 1
        try:
            r = self._llm.invoke([self._msg_sistema(content=sistema), self._msg_humano(content=usuario)])
            entrada, salida = self._extraer_tokens(r)
            if not entrada and not salida and r.content:
                # Groq no siempre informa usage: se estima (~4 caracteres/token)
                # y la métrica queda marcada como estimada.
                entrada = (len(sistema) + len(usuario)) // 4
                salida = len(r.content) // 4
                self.tokens_estimados = True
            self.tokens_entrada += entrada
            self.tokens_salida += salida
            return (r.content or "").strip()
        except Exception as e:
            self.fallback_usado = True
            self.motivo_fallback = f"{type(e).__name__}: {e}"
            return None

    def proponer(self, conflicto, agentes, ronda: int, terminos: str, max_rondas: int) -> str:
        """Redacta la propuesta de la ronda. El protocolo fija los términos."""
        partes = "; ".join(
            f"{a.nombre} (prioridad {a.prioridad}, deadline semana {a.semana_limite})"
            for a in agentes
        )
        if self.disponible:
            texto = self._invocar(
                SISTEMA_MEDIACION,
                f"Conflicto #{conflicto.id} de tipo {conflicto.tipo.value} sobre '{conflicto.recurso}'. "
                f"Partes: {partes}. Ronda {ronda} de {max_rondas}. "
                f"Términos que fija el protocolo: {terminos}. "
                "Redacta la propuesta formal del mediador (máximo 60 palabras).",
            )
            if texto:
                return f"Ronda {ronda}/{max_rondas} · propuesta LLM: {texto}"
        return f"Ronda {ronda}/{max_rondas} · mediador determinista: {terminos}."

    def redactar_acta(self, decisiones: dict) -> str:
        if self.disponible:
            texto = self._invocar(
                SISTEMA_ACTA,
                "Datos de la sesión de coordinación (JSON):\n"
                + json.dumps(decisiones, ensure_ascii=False, indent=2),
            )
            if texto:
                return texto
        return acta_determinista(decisiones)


def acta_determinista(decisiones: dict) -> str:
    """Acta de repuesto: markdown construido sin LLM a partir de las decisiones."""
    secciones = "\n".join(
        f"- **{sec}**: {', '.join(resp)}"
        for sec, resp in decisiones.get("secciones", {}).items()
    ) or "- (sin secciones asignadas)"
    recursos = "\n".join(
        f"- **{quien}**: {', '.join(rs)}"
        for quien, rs in decisiones.get("recursos_asignados", {}).items()
    ) or "- (sin recursos exclusivos asignados)"
    conflictos = "\n".join(
        f"- Conflicto #{c['id']} ({c['tipo']} sobre «{c['recurso']}»): {c['resolucion']}"
        for c in decisiones.get("conflictos", [])
    ) or "- Sin conflictos."
    return f"""# Acta de constitución del equipo (generada sin LLM)

## Tema aprobado
{decisiones.get('tema', '—')}

## Equipo y secciones
{secciones}

## Recursos asignados
{recursos}

## Conflictos y resoluciones
{conflictos}

## Acuerdos
- Cada sección tiene responsable definido y plazo asociado a su deadline.
- Los conflictos se resolvieron con la estrategia configurada y quedan trazados.
"""
