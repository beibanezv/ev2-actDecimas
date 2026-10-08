"""Equipo LLM (ChatGroq) con roles acotados + caídas deterministas.

Decisión de diseño (error #1 de la guía: *no usar LLM para todo*): el
protocolo multi-agente reparte las secciones, aplica la checklist de
revisión y decide cada conflicto en Python puro. Los LLM solo **producen
contenido** acotado:

* ``analizar``  → brief de hechos a partir del material real del proyecto;
* ``redactar``  → borrador del informe (solo puede usar el brief);
* ``revisar``   → motivos y correcciones puntuales (el veredicto
  ``aprobado`` lo fija la checklist determinista, no el LLM);
* ``arbitrar``  → veredicto final cuando se agota el tope de rondas;
* ``proponer``  → redacta las propuestas de cada ronda de negociación.

Sin clave, sin red o ante un error (p.ej. 429), cada método cae a su versión
determinista y la corrida se completa igual; las métricas registran llamadas,
tokens y el modo usado.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

MODELO_POR_DEFECTO = "openai/gpt-oss-20b"
RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"

SECCIONES_INFORME = ("Resumen ejecutivo", "Arquitectura", "Estado y pruebas",
                     "Riesgos y pendientes")

SISTEMA_ANALISTA = (
    "Eres analista de un equipo que documenta un proyecto de software. Lees el "
    "material entregado (markdowns, árbol de archivos y extractos de código) y "
    "produces un brief de HECHOS. Solo puedes afirmar lo que aparece en el "
    "material; si un dato no está, déjalo vacío. No inventes nada. "
    "Devuelves SOLO un JSON con las claves: proyecto, stack, componentes[], "
    "archivos_citados[], metricas[], huecos[]."
)

SISTEMA_REDACTOR = (
    "Eres redactor del equipo. Escribes un informe técnico en markdown para un "
    "proyecto de software, con exactamente estas cuatro secciones, en este "
    f"orden y con este nivel de encabezado: " +
    ", ".join(f"'## {s}'" for s in SECCIONES_INFORME) + ". "
    "Reglas: solo puedes usar datos del brief; NUNCA inventes archivos, "
    "funciones, métricas ni fechas. Si el brief no cubre algo, escribe "
    "'no documentado'. Máximo 400 palabras. Sin encabezado de nivel 1."
)

SISTEMA_REVISOR = (
    "Eres revisor del equipo. Recibes el informe y el resultado objetivo de una "
    "checklist (JSON con 'aprobado' y 'fallos'[]). Escribes, por cada fallo, un "
    "motivo concreto y una corrección accionable. Devuelves SOLO un JSON: "
    "{\"motivos\": [...], \"correcciones\": [{\"seccion\": \"...\", "
    "\"problema\": \"...\", \"solucion\": \"...\"}]}. No inventes problemas "
    "fuera de los fallos recibidos; como máximo dos observaciones de estilo."
)

SISTEMA_ARBITRO = (
    "Eres árbitro del equipo. El revisor y el redactor no llegaron a acuerdo "
    "dentro del tope de rondas. Dictas una resolución final breve (máximo 80 "
    "palabras): qué correcciones son innegociables, cuáles se aceptan como "
    "pendientes documentadas y bajo qué condición se aprueba el informe."
)


def _cargar_entorno() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=RUTA_ENV)
    except Exception:
        pass


def _parse_json(texto: str) -> dict | None:
    """Extrae el primer objeto JSON de la respuesta (tolera bloques ```json)."""
    if not texto:
        return None
    candidato = texto
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
    if m:
        candidato = m.group(1)
    else:
        i, j = texto.find("{"), texto.rfind("}")
        if i == -1 or j == -1 or j <= i:
            return None
        candidato = texto[i:j + 1]
    try:
        datos = json.loads(candidato)
        return datos if isinstance(datos, dict) else None
    except Exception:
        return None


class MediadorLLM:
    """Envuelve ChatGroq con roles acotados y caídas deterministas."""

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

    def _invocar(self, sistema: str, usuario: str, temperatura: float | None = None) -> str | None:
        self.llamadas += 1
        try:
            if temperatura is not None and hasattr(self._llm, "temperature"):
                # la revisión pide determinismo (veredictos estables)
                self._llm.temperature = temperatura
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

    # ---- rol 1: ANALISTA ---------------------------------------------------
    def analizar(self, material: dict) -> dict:
        """Brief de hechos a partir del material real del proyecto."""
        paquete = {
            "archivos_md": {k: v[:MAX_CARACTERES_MD] for k, v in material.get("md", {}).items()},
            "arbol": material.get("arbol", []),
            "extractos_codigo": {k: v[:MAX_CARACTERES_CODIGO] for k, v in material.get("codigo", {}).items()},
            "nota": "solo afirma lo que aparece en este material",
        }
        if self.disponible:
            texto = self._invocar(
                SISTEMA_ANALISTA,
                "Material del proyecto (JSON):\n" + json.dumps(paquete, ensure_ascii=False, indent=2))
            datos = _parse_json(texto) if texto else None
            if datos is not None:
                return _normalizar_brief(datos, material)
        return analizar_determinista(material)

    # ---- rol 2: REDACTOR ----------------------------------------------------
    def redactar(self, brief: dict, ronda: int = 1, correcciones: list[dict] | None = None) -> str:
        if self.disponible:
            extra = ""
            if correcciones:
                extra = ("\nCorrecciones obligatorias del revisor (aplica todas "
                         "las que puedas resolver con el brief):\n"
                         + json.dumps(correcciones, ensure_ascii=False, indent=2))
            texto = self._invocar(
                SISTEMA_REDACTOR,
                f"Brief (JSON):\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n"
                f"Ronda de redacción: {ronda}.{extra}")
            if texto:
                return texto
        return redactar_determinista(brief, correcciones)

    # ---- rol 3: REVISOR (veredicto lo fija la checklist) ---------------------
    def revisar(self, texto: str, checklist: dict) -> dict:
        """Motivos y correcciones puntuales; 'aprobado' viene del checklist."""
        if self.disponible:
            salida = self._invocar(
                SISTEMA_REVISOR,
                "Checklist objetivo (JSON):\n" + json.dumps(checklist, ensure_ascii=False) +
                "\n\nInforme a revisar:\n" + texto[:MAX_CARACTERES_INFORME],
                temperatura=0.1,
            )
            datos = _parse_json(salida) if salida else None
            if datos is not None:
                motivos = [str(x) for x in datos.get("motivos", []) if str(x).strip()]
                crudos = datos.get("correcciones", []) or []
                correcciones = [c for c in crudos if isinstance(c, dict) and c.get("solucion")]
                if motivos or checklist.get("fallos"):
                    return {"aprobado": bool(checklist.get("aprobado")),
                            "motivos": motivos or [f["descripcion"] for f in checklist.get("fallos", [])],
                            "correcciones": correcciones}
        return revisar_determinista(checklist)

    # ---- rol 4: ÁRBITRO -----------------------------------------------------
    def arbitrar(self, historial: list[dict]) -> str:
        rondas = len(historial)
        motivos = "; ".join(historial[-1].get("motivos", [])[:3]) if historial else "sin motivos"
        if self.disponible:
            texto = self._invocar(
                SISTEMA_ARBITRO,
                "Historial de revisión (JSON):\n" + json.dumps(historial, ensure_ascii=False, indent=2))
            if texto:
                return f"LAUDO DEL ÁRBITRO tras {rondas} rondas sin acuerdo: {texto}"
        return (f"LAUDO DEL ÁRBITRO tras {rondas} rondas sin acuerdo: el borrador se "
                f"acepta con advertencias. Motivos pendientes documentados: {motivos}.")

    # ---- negociación (las propuestas de cada ronda) --------------------------
    def proponer(self, conflicto, agentes, ronda: int, terminos: str, max_rondas: int) -> str:
        """Redacta la propuesta de la ronda. El protocolo fija los términos."""
        partes = "; ".join(
            f"{a.nombre} ({a.rol}, prioridad {a.prioridad}, deadline semana {a.semana_limite})"
            for a in agentes
        )
        if self.disponible:
            texto = self._invocar(
                "Eres el mediador del equipo de redacción. Redactas propuestas formales "
                "y breves (máximo 60 palabras), en español, sin inventar datos.",
                f"Conflicto #{conflicto.id} de tipo {conflicto.tipo.value} sobre "
                f"'{conflicto.recurso}'. Partes: {partes}. Ronda {ronda} de {max_rondas}. "
                f"Términos que fija el protocolo: {terminos}.",
            )
            if texto:
                return f"Ronda {ronda}/{max_rondas} · propuesta LLM: {texto}"
        return f"Ronda {ronda}/{max_rondas} · propuesta determinista: {terminos}."


# --- topes de lectura (error #5: el coste se mide y se acota) ------------------
MAX_CARACTERES_MD = 2600        # por archivo markdown
MAX_CARACTERES_CODIGO = 1200    # por archivo de código (solo con --codigo)
MAX_CARACTERES_INFORME = 6000   # texto del informe que se envía al revisor


def _normalizar_brief(datos: dict, material: dict) -> dict:
    """Fuerza las claves del brief y añade los archivos que realmente se leyeron."""
    leidos = list(material.get("md", {}).keys()) + list(material.get("codigo", {}).keys())
    return {
        "proyecto": str(datos.get("proyecto") or material.get("proyecto", "proyecto sin nombre")),
        "stack": [str(x) for x in datos.get("stack", [])][:6],
        "componentes": [str(x) for x in datos.get("componentes", [])][:10],
        "archivos_citados": sorted({str(x) for x in datos.get("archivos_citados", [])} |
                                   {Path(k).name for k in leidos}),
        "metricas": [str(x) for x in datos.get("metricas", [])][:6],
        "huecos": [str(x) for x in datos.get("huecos", [])][:6],
    }


def analizar_determinista(material: dict) -> dict:
    """Brief de repuesto: extrae títulos, bullets y señales sin LLM."""
    metricas, componentes, huecos, stack = [], [], [], []
    for nombre, texto in material.get("md", {}).items():
        for linea in texto.splitlines():
            t = linea.strip()
            if t.startswith("## ") and any(p in t.lower() for p in ("estado", "estructura", "limitac")):
                componentes.append(t[3:].strip())
            if t.startswith("- ") and any(p in t.lower() for p in ("prueba", "test", "cobertura", "%")):
                metricas.append(t[2:].strip())
            if any(p in t.lower() for p in ("pendiente", "no valida", "limitaci", "sin ")):
                huecos.append(t[:160])
            if any(p in t.lower() for p in ("python", "dependencia", "librer")):
                stack.append(t[:120])
    leidos = [Path(k).name for k in list(material.get("md", {})) + list(material.get("codigo", {}))]
    return {
        "proyecto": material.get("proyecto", "proyecto sin nombre"),
        "stack": stack[:6] or ["Python (biblioteca estándar)"],
        "componentes": componentes[:10] or ["sin componentes documentados"],
        "archivos_citados": leidos,
        "metricas": metricas[:6] or ["sin métricas documentadas"],
        "huecos": huecos[:6] or ["sin huecos declarados"],
    }


def redactar_determinista(brief: dict, correcciones: list[dict] | None = None) -> str:
    """Informe de repuesto: arma las 4 secciones con los datos del brief."""
    def viñetas(valores, vacio="no documentado"):
        vals = [str(v) for v in valores if str(v).strip()]
        return "\n".join(f"- {v}" for v in vals) if vals else f"- {vacio}"

    return f"""## Resumen ejecutivo

{viñetas([f"Proyecto: {brief.get('proyecto', 'no documentado')}"])}
- El presente informe describe el estado del proyecto a partir del material entregado por el Analista.

## Arquitectura

{viñetas(brief.get("componentes", []))}
- Stack declarado: {viñetas(brief.get("stack", []), 'no documentado')}

## Estado y pruebas

{viñetas(brief.get("metricas", []))}
- Archivos revisados: {viñetas(brief.get("archivos_citados", []), 'ninguno')}

## Riesgos y pendientes

{viñetas(brief.get("huecos", []))}
- Correcciones aplicadas en esta ronda: {len(correcciones or [])}."""


def revisar_determinista(checklist: dict) -> dict:
    """Veredicto de repuesto: motivos a partir de los fallos de la checklist."""
    fallos = checklist.get("fallos", [])
    motivos = [f.get("descripcion", "fallo sin descripción") for f in fallos]
    return {
        "aprobado": bool(checklist.get("aprobado")),
        "motivos": motivos,
        "correcciones": [
            {"seccion": f.get("seccion", "general"), "problema": f.get("descripcion", ""),
             "solucion": f.get("solucion", "corregir el fallo indicado")}
            for f in fallos
        ],
    }


def laudo_determinista(historial: list[dict]) -> str:
    rondas = len(historial)
    motivos = "; ".join(historial[-1].get("motivos", [])[:3]) if historial else "sin motivos"
    return (f"LAUDO DEL ÁRBITRO tras {rondas} rondas sin acuerdo: el borrador se "
            f"acepta con advertencias. Motivos pendientes documentados: {motivos}.")
