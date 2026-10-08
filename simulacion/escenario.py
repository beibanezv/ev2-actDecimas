"""Escenario «equipo que produce un entregable»: un informe técnico de un
proyecto real, escrito por un equipo de cuatro agentes con conflictos reales.

Fase 1  Briefing y reparto    → conflicto de PRIORIDAD (Analista y Redactor
                                se postulan a la misma sección)
Fase 2  Análisis del proyecto → el Analista lee el material real y comparte
                                un brief de hechos (anti-alucinación)
Fase 3  Redacción             → el Redactor escribe v1 usando SOLO el brief
Fase 4  Revisión              → el Revisor verifica cada borrador contra una
                                checklist objetiva; cada rechazo abre un
                                conflicto de OBJETIVO que se resuelve con la
                                estrategia configurada. Tope duro: 3 rondas.
Fase 5  Consolidación         → informe final + laudo del árbitro si no hubo
                                acuerdo + métricas de la corrida

El veredicto «aprobado/rechazado» lo fija la **checklist determinista**
(secciones exigidas, palabras mínimas, sin placeholders, archivos citados
verificables); el LLM aporta motivos y correcciones, no el veredicto.
"""

from __future__ import annotations

import random
import re
import time
from pathlib import Path

from .agentes import MiembroEquipo
from .bitacora import BITACORA
from .conflictos import (
    EstrategiaResolucion,
    ResolvedorConflictos,
    TipoConflicto,
    MAX_RONDAS_NEGOCIACION,
)
from .coordinacion import Coordinador, TipoMensaje
from .mediador_llm import (
    MAX_CARACTERES_CODIGO,
    MAX_CARACTERES_MD,
    analizar_determinista,
    laudo_determinista,
    redactar_determinista,
    revisar_determinista,
)

# Secciones exigidas al informe y la capacidad que se necesita para escribirlas.
SECCIONES_INFORME = [
    {"id": "Resumen ejecutivo", "capacidad": "resumen"},
    {"id": "Arquitectura", "capacidad": "redaccion"},
    {"id": "Estado y pruebas", "capacidad": "analisis"},
    {"id": "Riesgos y pendientes", "capacidad": "revision"},
]
IDS_SECCIONES = [s["id"] for s in SECCIONES_INFORME]

# Umbrales de la checklist objetiva (determinista, auditable).
MIN_PALABRAS_SECCION = 60
MIN_ARCHIVOS_CITADOS = 2
PLACEHOLDERS = ("TODO", "FIXME", "[rellenar]", "lorem", "XXX", "TBD")

CARPETA_EJEMPLO = "ejemplo-proyecto"
RAIZ_EJEMPLO = Path(__file__).resolve().parent.parent / CARPETA_EJEMPLO


# --- lectura del proyecto objetivo -------------------------------------------
def leer_proyecto(ruta: str | Path, incluir_codigo: bool = False) -> dict:
    """Material que el Analista entrega al equipo: markdowns, árbol y (opcional)
    extractos de código, siempre con tope de caracteres por archivo."""
    raiz = Path(ruta)
    if not raiz.exists():
        raise FileNotFoundError(f"no existe la carpeta del proyecto: {raiz}")
    md: dict[str, str] = {}
    for p in sorted(raiz.rglob("*.md")):
        if ".git" in p.parts:
            continue
        try:
            md[p.name] = p.read_text(encoding="utf-8", errors="replace")[:MAX_CARACTERES_MD]
        except Exception:
            continue
    codigo: dict[str, str] = {}
    if incluir_codigo:
        for p in sorted(raiz.rglob("*.py")):
            if any(parte in (".git", "__pycache__", ".venv") for parte in p.parts):
                continue
            try:
                codigo[p.name] = p.read_text(encoding="utf-8", errors="replace")[:MAX_CARACTERES_CODIGO]
            except Exception:
                continue
    arbol = [
        str(p.relative_to(raiz)).replace("\\", "/")
        for p in sorted(raiz.rglob("*"))
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts
    ]
    return {"proyecto": raiz.name, "md": md, "codigo": codigo, "arbol": arbol}


# --- checklist determinista ----------------------------------------------------
def archivos_verificables(material: dict) -> set[str]:
    """Archivos que el lector puede comprobar: los del árbol/md/código leídos
    más los que los propios markdowns mencionan (p.ej. biblioteca.json).
    Cualquier otro .md/.py/.json citado por el informe es alucinación."""
    reales = {Path(k).name for k in material.get("md", {})} | \
             set(material.get("codigo", {}).keys()) | set(material.get("arbol", []))
    mencionados = set()
    for texto in material.get("md", {}).values():
        mencionados |= set(re.findall(r"[\w\-/\.]+\.(?:md|py|json|ya?ml|txt)", texto))
    return reales | {Path(m).name for m in mencionados}


def secciones_del_texto(texto: str) -> dict[str, str]:
    """Divide el informe por encabezados '## '."""
    partes, actual = {}, None
    for linea in texto.splitlines():
        if linea.startswith("## "):
            actual = linea[3:].strip()
            partes[actual] = []
        elif actual is not None:
            partes[actual].append(linea)
    return {k: "\n".join(v) for k, v in partes.items()}


def checklist_determinista(texto: str, brief: dict, material: dict) -> dict:
    """Evalúa el borrador con criterios objetivos. Es la fuente de la verdad."""
    fallos: list[dict] = []
    partes = secciones_del_texto(texto)
    for sec in IDS_SECCIONES:
        if sec not in partes:
            fallos.append({"seccion": sec, "descripcion": f"falta la sección '{sec}'",
                           "solucion": f"añade la sección '## {sec}'"})
        elif len(partes[sec].split()) < MIN_PALABRAS_SECCION:
            fallos.append({"seccion": sec,
                           "descripcion": f"la sección '{sec}' tiene menos de {MIN_PALABRAS_SECCION} palabras",
                           "solucion": f"amplía '{sec}' con datos del brief"})
    for ph in PLACEHOLDERS:
        if ph in texto:
            fallos.append({"seccion": "general",
                           "descripcion": f"queda un placeholder '{ph}' en el informe",
                           "solucion": "reemplaza el placeholder por contenido real"})
            break
    citados = set(re.findall(r"[\w\-/\.]+\.(?:md|py|json)", texto))
    reales = archivos_verificables(material)
    inventados = sorted(c for c in citados if Path(c).name not in reales)
    if inventados:
        fallos.append({"seccion": "general",
                       "descripcion": f"cita archivos no verificables: {', '.join(inventados[:4])}",
                       "solucion": "cita solo archivos del material entregado"})
    if len(citados & reales) < MIN_ARCHIVOS_CITADOS:
        fallos.append({"seccion": "general",
                       "descripcion": f"cita menos de {MIN_ARCHIVOS_CITADOS} archivos reales del proyecto",
                       "solucion": "menciona archivos reales en Arquitectura y Estado"})
    return {"aprobado": not fallos, "fallos": fallos}


# --- equipo --------------------------------------------------------------------
def construir_equipo() -> tuple[Coordinador, dict[str, MiembroEquipo]]:
    coord = Coordinador("Coordinador del equipo de redacción")
    ana = MiembroEquipo("ana", "Analista", "analista", ("analisis", "lectura_codigo", "resumen"),
                        prioridad=3, semana_limite=5,
                        postulaciones=("Resumen ejecutivo", "Estado y pruebas"))
    red = MiembroEquipo("red", "Redactor", "redactor", ("redaccion", "resumen"),
                        prioridad=2, semana_limite=5,
                        postulaciones=("Resumen ejecutivo", "Arquitectura"))
    rev = MiembroEquipo("rev", "Revisor", "revisor", ("revision", "verificacion"),
                        prioridad=1, semana_limite=6,
                        postulaciones=("Riesgos y pendientes",))
    for m in (ana, red, rev):
        coord.registrar_agente(m)
    return coord, {"ana": ana, "red": red, "rev": rev}


def _accion_de_resolucion(conflicto) -> str:
    """Traduce el resultado del conflicto redactor/revisor en una acción concreta."""
    if conflicto.asignado_a == "":
        return "corregir_mitad"           # compromiso del ResolvedorConflictos
    if "arbitraje" in (conflicto.resolucion or "").lower() and "forzado" in (conflicto.resolucion or "").lower():
        return "corregir_minimas"         # tope de rondas agotado en la negociación
    if conflicto.asignado_a == "rev":
        return "corregir_todo"            # ganó el revisor
    return "aceptar"                      # ganó el redactor


def ejecutar(ruta_proyecto: str | Path = RAIZ_EJEMPLO,
             estrategia: EstrategiaResolucion = EstrategiaResolucion.NEGOCIACION,
             semilla: int = 42, mediador=None,
             max_rondas: int = MAX_RONDAS_NEGOCIACION,
             incluir_codigo: bool = False) -> dict:
    raiz = Path(ruta_proyecto)
    rng = random.Random(semilla)
    t0 = time.perf_counter()
    coord, equipo = construir_equipo()
    ana, red, rev = equipo["ana"], equipo["red"], equipo["rev"]
    resolver = ResolvedorConflictos(rng=rng)
    for m in (ana, red, rev):
        resolver.registrar_agente(m)

    BITACORA.log("=" * 72)
    BITACORA.log(f"EQUIPO QUE PRODUCE UN ENTREGABLE · proyecto={raiz.name} · "
                 f"estrategia={estrategia.value} · semilla={semilla}")
    BITACORA.log(f"Equipo LLM: {mediador.modo if mediador else 'ninguno (corrida determinista)'}")
    BITACORA.log(f"Tope de rondas de revisión: {max_rondas}")
    BITACORA.log("=" * 72)

    # ---- Fase 1: briefing y reparto de secciones ---------------------------
    BITACORA.log("\n[Fase 1] El Coordinador recibe la solicitud y divide el informe")
    coord.anunciar_tarea(f"Informe técnico de {raiz.name}", IDS_SECCIONES)
    coord.broadcast(TipoMensaje.CONSULTA, "¿A qué secciones se postulan?")
    for m in (ana, red, rev):
        m.enviar(coord.id, TipoMensaje.RESPUESTA,
                 f"Me postulo a {m.postular(IDS_SECCIONES)}")
    coord.procesar_todos()

    asignacion: dict[str, list[str]] = {}
    for sec in IDS_SECCIONES:
        candidatos = [m for m in (ana, red, rev) if sec in m.postular(IDS_SECCIONES)]
        if len(candidatos) == 1:
            ganador = candidatos[0]
        elif not candidatos:
            capacidad = next(s["capacidad"] for s in SECCIONES_INFORME if s["id"] == sec)
            ganador = coord.asignar_por_capacidad(capacidad)
            if ganador is not None and ganador not in (ana, red, rev):
                ganador = {"resumen": red, "redaccion": red, "analisis": ana,
                           "revision": rev}[capacidad]
        else:
            conflicto = resolver.detectar_conflicto_prioridad(sec, candidatos)
            BITACORA.log(f"  ⚠ Conflicto detectado: {conflicto.descripcion}")
            resolver.resolver(conflicto, estrategia, mediador)
            ganador = equipo.get(conflicto.asignado_a)
            if ganador is None:  # compromiso: co-autoría
                asignacion[sec] = [a.id for a in candidatos]
                for a in candidatos:
                    a.seccion_asignada = sec
                    a.enviar(coord.id, TipoMensaje.ACEPTACION, f"Co-escribo '{sec}'")
                BITACORA.log(f"  ✓ {sec} → {', '.join(a.nombre for a in candidatos)} (co-autoría)")
                continue
        if ganador is None:
            BITACORA.log(f"  ✗ {sec} quedó sin responsable (no había capacidad)")
            continue
        asignacion[sec] = [ganador.id]
        ganador.seccion_asignada = sec
        BITACORA.log(f"  ✓ {sec} → {ganador.nombre}")
        ganador.enviar(coord.id, TipoMensaje.ACEPTACION, f"Tomo '{sec}'")

    # ---- Fase 2: análisis del proyecto --------------------------------------
    BITACORA.log("\n[Fase 2] El Analista lee el proyecto objetivo y extrae el brief")
    material = leer_proyecto(raiz, incluir_codigo=incluir_codigo)
    BITACORA.log(f"  Material leído: {len(material['md'])} markdown(s), "
                 f"{len(material['codigo'])} código(s), {len(material['arbol'])} archivos en el árbol")
    if mediador:
        brief = mediador.analizar(material)
        BITACORA.log(f"  Brief (modo {mediador.modo}): {brief.get('proyecto')}")
    else:
        brief = analizar_determinista(material)
        BITACORA.log("  Brief (determinista): extraído de títulos y bullets")
    ana.compartir_conocimiento(
        [red.id, rev.id, coord.id], "brief",
        f"archivos citados: {', '.join(brief.get('archivos_citados', [])[:6])}")

    # ---- Fase 3: redacción del borrador v1 ----------------------------------
    BITACORA.log("\n[Fase 3] El Redactor escribe el borrador v1 con el brief")
    if mediador:
        borrador = mediador.redactar(brief, ronda=1)
    else:
        borrador = redactar_determinista(brief)
    red.enviar(rev.id, TipoMensaje.PROPUESTA, "Borrador v1 listo para revisión")
    BITACORA.log(f"  Borrador v1: {len(borrador.split())} palabras")

    # ---- Fase 4: revisión con tope duro de rondas ---------------------------
    BITACORA.log("\n[Fase 4] El Revisor verifica cada borrador contra la checklist")
    veredictos: list[dict] = []
    aprobado = False
    acciones: list[str] = []
    for ronda in range(1, max_rondas + 1):
        checklist = checklist_determinista(borrador, brief, material)
        veredicto = mediador.revisar(borrador, checklist) if mediador else revisar_determinista(checklist)
        veredicto["ronda"] = ronda
        veredictos.append(veredicto)
        if veredicto["aprobado"]:
            BITACORA.log(f"  ✓ Ronda {ronda}: APROBADO (checklist pasa)")
            aprobado = True
            break
        fallos = checklist["fallos"]
        motivos = "; ".join(veredicto.get("motivos", [])[:3])
        BITACORA.log(f"  ✗ Ronda {ronda}: RECHAZADO — {len(fallos)} fallo(s) de checklist. {motivos}")

        # El rechazo del revisor abre un conflicto REAL de objetivo.
        conflicto = resolver.nuevo_conflicto(
            TipoConflicto.OBJETIVO, [red, rev], f"informe_v{ronda}",
            f"El Revisor rechaza el borrador v{ronda} ({len(fallos)} fallos de "
            f"checklist); el Redactor quiere entregarlo.", severidad=3)
        resolver.resolver(conflicto, estrategia, mediador)
        accion = _accion_de_resolucion(conflicto)
        acciones.append(accion)
        BITACORA.log(f"  ⚖ Resolución del conflicto: {conflicto.resolucion}")
        if accion == "aceptar":
            BITACORA.log("  → Se acepta el borrador actual (ganó el Redactor)")
            break
        correcciones = veredicto.get("correcciones", [])
        if accion == "corregir_mitad" and len(correcciones) > 1:
            correcciones = correcciones[:(len(correcciones) + 1) // 2]
        if accion == "corregir_minimas" and len(correcciones) > 1:
            correcciones = correcciones[:1]
        BITACORA.log(f"  → Se aplican {len(correcciones)} corrección(es) y se reescribe")
        if mediador:
            borrador = mediador.redactar(brief, ronda=ronda + 1, correcciones=correcciones)
        else:
            borrador = redactar_determinista(brief, correcciones)

    # ---- Fase 5: consolidación ----------------------------------------------
    laudo = ""
    if not aprobado and not any(a == "aceptar" for a in acciones):
        BITACORA.log("\n[Fase 5] Tope de rondas agotado: el árbitro dicta resolución")
        laudo = mediador.arbitrar(veredictos) if mediador else laudo_determinista(veredictos)
        BITACORA.log(f"  {laudo}")
    elif not aprobado:
        laudo = "Aceptado por decisión del equipo antes del tope, con fallos de checklist pendientes."

    informe_final = borrador.rstrip() + "\n"
    if laudo:
        informe_final += f"\n---\n\n## Resolución final\n\n{laudo}\n"

    BITACORA.log("\n[Fase 5] Informe consolidado")
    for sec, ids in asignacion.items():
        BITACORA.log(f"  {sec}: {', '.join(equipo[i].nombre for i in ids)}")
    BITACORA.log(f"  Rondas de revisión usadas: {len([v for v in veredictos if not v['aprobado']])}"
                 f"/{max_rondas} · aprobado: {aprobado}")

    decisiones = {
        "proyecto": raiz.name,
        "estrategia": estrategia.value,
        "secciones": {sec: [equipo[i].nombre for i in ids] for sec, ids in asignacion.items()},
        "brief": brief,
        "veredictos": veredictos,
        "acciones": acciones,
        "aprobado": aprobado,
        "informe": informe_final,
    }
    metricas = {
        "proyecto": raiz.name,
        "estrategia": estrategia.value,
        "semilla": semilla,
        "mediador": mediador.modo if mediador else "sin equipo LLM",
        "mediador_error": mediador.motivo_fallback if (mediador and mediador.fallback_usado) else "",
        "llamadas_mediador": mediador.llamadas if mediador else 0,
        "tokens_mediador_entrada": mediador.tokens_entrada if mediador else 0,
        "tokens_mediador_salida": mediador.tokens_salida if mediador else 0,
        "tokens_estimados": mediador.tokens_estimados if mediador else False,
        "mensajes": len(coord.registro_mensajes),
        "conflictos_detectados": len(resolver.conflictos),
        "conflictos_resueltos": sum(1 for c in resolver.conflictos if c.resuelto),
        "rondas_negociacion": sum(c.rondas for c in resolver.conflictos),
        "rondas_revision": len([v for v in veredictos if not v["aprobado"]]),
        "aprobado": aprobado,
        "segundos": round(time.perf_counter() - t0, 3),
    }
    return {
        "decisiones": decisiones,
        "metricas": metricas,
        "reportes": {
            "comunicacion": coord.generar_reporte_comunicacion(),
            "conflictos": resolver.generar_reporte(),
        },
    }
