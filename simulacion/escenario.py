"""Escenario «informe académico grupal»: cuatro fases con conflictos reales.

Fase 1  Reparto de secciones       → conflicto de PRIORIDAD (dos quieren redactar)
Fase 2  Votación del tema          → conflicto de OBJETIVO si hay empate
Fase 3  Recursos exclusivos        → conflicto de RECURSO (base de datos y sala)
Fase 4  Slot de revisión           → conflicto TEMPORAL (deadlines traslapados)

Al terminar, consolida el plan (tema, sección→responsable, recursos,
cronograma), redacta el acta y calcula las métricas de la corrida.
"""

from __future__ import annotations

import random
import time

from .agentes import Estudiante
from .bitacora import BITACORA
from .conflictos import EstrategiaResolucion, ResolvedorConflictos, TipoConflicto
from .coordinacion import Coordinador, TipoMensaje
from .mediador_llm import acta_determinista

TEMAS = [
    "Impacto de los agentes de IA en la evaluación formativa",
    "Riesgos de sesgo en modelos de lenguaje educativos",
    "Tutores LLM en educación media: oportunidades y límites",
]

SECCIONES = [
    {"id": "revision_bibliografica", "nombre": "Revisión bibliográfica", "capacidad": "busqueda_fuentes"},
    {"id": "analisis_datos", "nombre": "Análisis de datos", "capacidad": "estadistica"},
    {"id": "redaccion_informe", "nombre": "Redacción del informe", "capacidad": "redaccion"},
]
SECCIONES_POR_ID = {s["id"]: s for s in SECCIONES}

RECURSOS_EXCLUSIVOS = ("acceso_base_datos", "software_estadistico", "biblioteca_digital", "sala_de_trabajo")
SLOTS = {"revision_con_profesor": 1}  # capacidad 1 → conflicto temporal garantizado

# Solicitudes declaradas por agente (recursos y slots).
# El slot 'revision_con_profesor' (capacidad 1) lo piden dos agentes con
# deadlines distintos → conflicto TEMPORAL garantizado.
SOLICITUDES = {
    "inv": ("acceso_base_datos", "revision_con_profesor"),
    "ana": ("acceso_base_datos", "software_estadistico", "sala_de_trabajo", "revision_con_profesor"),
    "red": ("biblioteca_digital", "sala_de_trabajo"),
}


def construir_equipo() -> tuple[Coordinador, list[Estudiante]]:
    coord = Coordinador()
    estudiantes = [
        Estudiante("inv", "Investigador", "investigador", ("busqueda_fuentes", "redaccion"),
                   prioridad=2, semana_limite=3,
                   afinidad_temas=(1, 0, 2),
                   preferencias_seccion=("redaccion_informe", "revision_bibliografica")),
        Estudiante("ana", "Analista", "analista", ("estadistica", "analisis"),
                   prioridad=1, semana_limite=5,
                   afinidad_temas=(0, 2, 1),
                   preferencias_seccion=("analisis_datos",)),
        Estudiante("red", "Redactor", "redactor", ("redaccion",),
                   prioridad=3, semana_limite=6,
                   afinidad_temas=(2, 1, 0),
                   preferencias_seccion=("redaccion_informe",)),
    ]
    for e in estudiantes:
        coord.registrar_agente(e)
    return coord, estudiantes


def ejecutar(estrategia: EstrategiaResolucion, semilla: int = 42, mediador=None) -> dict:
    rng = random.Random(semilla)
    t0 = time.perf_counter()
    coord, estudiantes = construir_equipo()
    resolver = ResolvedorConflictos(rng=rng)
    for e in estudiantes:
        resolver.registrar_agente(e)
    for r in RECURSOS_EXCLUSIVOS:
        resolver.agregar_recurso(r)
    for sid, cap in SLOTS.items():
        resolver.agregar_slot(sid, cap)
    agentes = {a.id: a for a in estudiantes}
    ids_secciones = [s["id"] for s in SECCIONES]

    BITACORA.log("=" * 72)
    BITACORA.log(f"SISTEMA DE COLABORACIÓN ACADÉMICA · estrategia={estrategia.value} · semilla={semilla}")
    BITACORA.log(f"Mediador: {mediador.modo if mediador else 'ninguno (corrida determinista)'}")
    BITACORA.log("=" * 72)

    # ---- Fase 1: reparto de secciones ------------------------------------
    BITACORA.log("\n[Fase 1] Reparto de secciones del informe")
    coord.anunciar_tarea("Informe académico grupal", ids_secciones)
    coord.broadcast(TipoMensaje.CONSULTA, "¿Qué sección prefieren? Respondan con su primera opción.")
    for a in estudiantes:
        a.enviar(coord.id, TipoMensaje.RESPUESTA, f"Prefiero '{a.elegir_seccion(ids_secciones)}'")
    coord.procesar_todos()

    asignacion: dict[str, list[str]] = {}
    for s in SECCIONES:
        sid, nombre_seccion = s["id"], s["nombre"]
        candidatos = [a for a in estudiantes if a.elegir_seccion(ids_secciones) == sid]
        if len(candidatos) == 1:
            ganador = candidatos[0]
            asignacion[sid] = [ganador.id]
            ganador.seccion_asignada = sid
            BITACORA.log(f"  ✓ {nombre_seccion} → {ganador.nombre}")
            ganador.enviar(coord.id, TipoMensaje.ACEPTACION, f"Tomo '{nombre_seccion}'")
        elif not candidatos:
            ganador = coord.asignar_por_capacidad(s["capacidad"])
            if ganador is not None:
                asignacion[sid] = [ganador.id]
                ganador.seccion_asignada = sid
                BITACORA.log(f"  ✓ {nombre_seccion} → {ganador.nombre} (asignado por capacidad)")
                ganador.enviar(coord.id, TipoMensaje.ACEPTACION, f"Tomo '{nombre_seccion}'")
        else:
            conflicto = resolver.detectar_conflicto_prioridad(sid, candidatos)
            BITACORA.log(f"  ⚠ Conflicto detectado: {conflicto.descripcion}")
            resolver.resolver(conflicto, estrategia, mediador)
            if conflicto.asignado_a:
                asignacion[sid] = [conflicto.asignado_a]
                agentes[conflicto.asignado_a].seccion_asignada = sid
                agentes[conflicto.asignado_a].enviar(coord.id, TipoMensaje.ACEPTACION, f"Tomo '{nombre_seccion}'")
            else:  # compromiso: co-autoría
                asignacion[sid] = [a.id for a in candidatos]
                for a in candidatos:
                    a.seccion_asignada = sid
                    a.enviar(coord.id, TipoMensaje.ACEPTACION, f"Co-escribo '{nombre_seccion}'")

    # ---- Fase 2: votación del tema ---------------------------------------
    BITACORA.log("\n[Fase 2] Votación del tema del informe (3 opciones)")
    coord.broadcast(TipoMensaje.CONSULTA, "Voten por el tema del informe.")
    voto = coord.votacion_multiple("Tema del informe", TEMAS)
    for aid, opcion in voto["votos"].items():
        BITACORA.log(f"  🗳 {agentes[aid].nombre} vota por «{opcion}»")
    BITACORA.log(f"  Conteo: {voto['conteo']}")
    tema_ganador = voto["ganador"]
    if tema_ganador is None:
        cempate = resolver.nuevo_conflicto(
            TipoConflicto.OBJETIVO, estudiantes, "tema_del_informe",
            f"La votación empató entre {len(voto['empatados'])} temas: {'; '.join(voto['empatados'])}", 2)
        resolver.resolver(cempate, estrategia, mediador)
        defensor = agentes.get(cempate.asignado_a)
        if defensor is not None:
            tema_ganador = defensor.votar(TEMAS)
        else:  # compromiso sin ganador único: desempate documentado
            tema_ganador = voto["empatados"][0]
        BITACORA.log(f"  ⚖ Empate resuelto → «{tema_ganador}»")
    else:
        BITACORA.log(f"  ✓ Tema ganador: «{tema_ganador}»")

    # ---- Fase 3: recursos exclusivos --------------------------------------
    BITACORA.log("\n[Fase 3] Asignación de recursos exclusivos")
    for aid, rids in SOLICITUDES.items():
        for r in rids:
            agentes[aid].solicitar_recurso(r)
            agentes[aid].enviar(coord.id, TipoMensaje.PETICION, f"Solicito '{r}'")
    coord.procesar_todos()
    for c in resolver.detectar_conflicto_recurso():
        BITACORA.log(f"  ⚠ Conflicto detectado: {c.descripcion}")
        resolver.resolver(c, estrategia, mediador)

    # ---- Fase 4: conflicto temporal ---------------------------------------
    BITACORA.log("\n[Fase 4] Conflicto temporal: slot de revisión con el profesor")
    for c in resolver.detectar_conflicto_temporal():
        BITACORA.log(f"  ⚠ Conflicto detectado: {c.descripcion}")
        resolver.resolver(c, estrategia, mediador)

    # ---- Fase 5: consolidado ----------------------------------------------
    BITACORA.log("\n[Fase 5] Plan consolidado")
    BITACORA.log(f"  Tema: {tema_ganador}")
    for sid, ids in asignacion.items():
        nombres = ", ".join(agentes[i].nombre for i in ids)
        BITACORA.log(f"  {SECCIONES_POR_ID[sid]['nombre']}: {nombres}")
    for a in estudiantes:
        if a.recursos:
            BITACORA.log(f"  {a.nombre} obtiene: {', '.join(a.recursos)} (deadline semana {a.semana_limite})")

    decisiones = {
        "tema": tema_ganador,
        "secciones": {SECCIONES_POR_ID[sid]["nombre"]: [agentes[i].nombre for i in ids]
                      for sid, ids in asignacion.items()},
        "recursos_asignados": {a.nombre: list(a.recursos) for a in estudiantes if a.recursos},
        "deadlines": {a.nombre: f"semana {a.semana_limite}" for a in estudiantes},
        "votacion": {"conteo": voto["conteo"], "empate": voto["empate"]},
        "conflictos": [
            {"id": c.id, "tipo": c.tipo.value, "recurso": c.recurso, "estrategia": c.estrategia,
             "rondas": c.rondas, "resuelto": c.resuelto, "resolucion": c.resolucion}
            for c in resolver.conflictos
        ],
    }
    acta = mediador.redactar_acta(decisiones) if mediador else acta_determinista(decisiones)

    metricas = {
        "estrategia": estrategia.value,
        "semilla": semilla,
        "mediador": mediador.modo if mediador else "sin mediador",
        "mediador_error": mediador.motivo_fallback if (mediador and mediador.fallback_usado) else "",
        "llamadas_mediador": mediador.llamadas if mediador else 0,
        "tokens_mediador_entrada": mediador.tokens_entrada if mediador else 0,
        "tokens_mediador_salida": mediador.tokens_salida if mediador else 0,
        "tokens_estimados": mediador.tokens_estimados if mediador else False,
        "mensajes": len(coord.registro_mensajes),
        "conflictos_detectados": len(resolver.conflictos),
        "conflictos_resueltos": sum(1 for c in resolver.conflictos if c.resuelto),
        "rondas_negociacion": sum(c.rondas for c in resolver.conflictos),
        "segundos": round(time.perf_counter() - t0, 3),
        "asignaciones": {
            c.recurso: (agentes[c.asignado_a].nombre if c.asignado_a else "compartido")
            for c in resolver.conflictos
        },
    }
    return {
        "decisiones": decisiones,
        "acta": acta,
        "metricas": metricas,
        "reportes": {
            "comunicacion": coord.generar_reporte_comunicacion(),
            "conflictos": resolver.generar_reporte(),
        },
    }
