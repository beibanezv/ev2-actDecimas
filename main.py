"""CLI del sistema multi-agente que produce un entregable (actividad IL2.3).

Ejemplos::

    # demo lista para usar: proyecto de ejemplo incluido, mediador LLM real
    python main.py --proyecto ejemplo-proyecto --estrategia negociacion

    # apunta a cualquier proyecto real (solo lee .md salvo --codigo)
    python main.py --proyecto ../ep1-veterinaria-agente --codigo

    # corrida determinista, sin red ni clave
    python main.py --proyecto ejemplo-proyecto --llm no

    # comparativa de las 6 estrategias (determinista, barata)
    python main.py --comparar
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from simulacion import escenario
from simulacion.bitacora import BITACORA
from simulacion.conflictos import EstrategiaResolucion
from simulacion.mediador_llm import MODELO_POR_DEFECTO, MediadorLLM

RAIZ = Path(__file__).resolve().parent
CARPETA_EVIDENCIA = RAIZ / "evidencia"


def slug(nombre: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in nombre.lower()).strip("-") or "proyecto"


def formato_metricas(m: dict) -> str:
    lineas = ["## Métricas de la corrida", ""]
    for k, v in m.items():
        lineas.append(f"- **{k}**: {v}")
    return "\n".join(lineas)


def resumen_veredictos(resultado: dict) -> str:
    lineas = ["## Veredictos del revisor", ""]
    for v in resultado["decisiones"]["veredictos"]:
        estado = "APROBADO" if v["aprobado"] else "RECHAZADO"
        motivos = "; ".join(v.get("motivos", [])[:3]) or "—"
        lineas.append(f"- Ronda {v['ronda']}: **{estado}** — {motivos}")
    laudo = [b for b in resultado["decisiones"]["informe"].splitlines()
             if "LAUDO" in b or "Aceptado por" in b]
    if laudo:
        lineas += ["", laudo[0]]
    return "\n".join(lineas)


def escribir_evidencia(nombre: str, contenido: str) -> Path:
    CARPETA_EVIDENCIA.mkdir(exist_ok=True)
    ruta = CARPETA_EVIDENCIA / nombre
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def documento_corrida(titulo: str, resultado: dict, transcripcion: str, ahora: str) -> str:
    m = resultado["metricas"]
    return "\n".join([
        f"# {titulo}",
        "",
        f"Generado: {ahora} · equipo LLM: {m['mediador']}",
        "",
        "## Transcripción de la simulación",
        "",
        "```text",
        transcripcion,
        "```",
        "",
        "## Reporte de comunicación",
        "",
        "```text",
        resultado["reportes"]["comunicacion"],
        "```",
        "",
        "## Reporte de conflictos",
        "",
        "```text",
        resultado["reportes"]["conflictos"],
        "```",
        "",
        formato_metricas(m),
        "",
        resumen_veredictos(resultado),
        "",
    ])


def tabla_comparativa(filas: list[dict], ahora: str) -> str:
    lineas = [
        "# Comparativa de estrategias de resolución del desacuerdo",
        "",
        f"Generado: {ahora}. Corridas deterministas (sin equipo LLM) para aislar "
        "el efecto de la estrategia sobre el MISMO informe borrador.",
        "",
        "| Estrategia | Rondas revisión | Aprobado | Acciones del revisor | "
        "Conflictos | Rondas neg. | Segundos |",
        "|---|---|---|---|---|---|---|",
    ]
    for m in filas:
        lineas.append(
            f"| {m['estrategia']} | {m['rondas_revision']} | "
            f"{'sí' if m['aprobado'] else 'no'} | "
            f"{', '.join(m.get('_acciones', [])) or '—'} | "
            f"{m['conflictos_resueltos']}/{m['conflictos_detectados']} | "
            f"{m['rondas_negociacion']} | {m['segundos']} |"
        )
    lineas += [
        "",
        "**Lectura:** el escenario y el borrador son idénticos entre estrategias; "
        "lo que cambia es la acción que toma el equipo cuando el revisor rechaza. "
        "El Revisor es el gate de calidad (prioridad 1): las estrategias por "
        "prioridad y arbitraje le dan la razón y el Redactor corrige TODO hasta "
        "agotar el tope de 3 rondas; el compromiso y la negociación corrigen la "
        "mitad de los puntos; primero-en-llegada deja ganar al Redactor (llegó "
        "primero) y acepta el borrador con fallos; la votación depende del "
        "sorteo con semilla. Ninguna estrategia cambia los hechos: decide quién "
        "impone su criterio y cuántas rondas cuesta.",
        "",
    ]
    return "\n".join(lineas)


def main() -> None:
    try:  # consola en UTF-8 cuando se puede (Windows usa cp1252 por defecto)
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(
        description="Equipo multi-agente que produce un informe técnico de un proyecto")
    parser.add_argument("--proyecto", default=str(escenario.RAIZ_EJEMPLO),
                        help="carpeta del proyecto a documentar (default: ejemplo-proyecto)")
    parser.add_argument("--estrategia", default="negociacion",
                        choices=[e.value for e in EstrategiaResolucion],
                        help="cómo se resuelve el desacuerdo revisor/redactor")
    parser.add_argument("--rondas", type=int, default=3,
                        help="tope duro de rondas de revisión (máx 3)")
    parser.add_argument("--seed", "--semilla", dest="semilla", type=int, default=42,
                        help="semilla del generador aleatorio (reproducibilidad)")
    parser.add_argument("--llm", choices=["auto", "si", "no"], default="auto",
                        help="auto/si: usa ChatGroq si hay clave; no: determinsta puro")
    parser.add_argument("--modelo", default=MODELO_POR_DEFECTO)
    parser.add_argument("--codigo", action="store_true",
                        help="incluir extractos de código .py en el análisis (cuesta más tokens)")
    parser.add_argument("--comparar", action="store_true",
                        help="corre las 6 estrategias con la misma semilla y escribe la comparativa")
    args = parser.parse_args()

    mediador = MediadorLLM(modelo=args.modelo, activo=args.llm != "no")
    if args.llm == "no":
        BITACORA.log("Equipo LLM desactivado (--llm no): corrida determinista.")
    elif not mediador.disponible:
        BITACORA.log(f"Equipo LLM no disponible ({mediador.motivo_fallback}); "
                     "se usan los redactores deterministas.")
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    if args.comparar:
        filas: list[dict] = []
        for e in EstrategiaResolucion:
            resultado = escenario.ejecutar(
                args.proyecto, e, args.semilla, mediador=None,
                max_rondas=min(args.rondas, 3), incluir_codigo=False)
            transcripcion = BITACORA.volcado()
            BITACORA.limpiar()
            m = resultado["metricas"]
            m["_acciones"] = resultado["decisiones"]["acciones"]
            filas.append(m)
            escribir_evidencia(
                f"corrida-{e.value}-seed{args.semilla}.md",
                documento_corrida(
                    f"Corrida — estrategia {e.value} (proyecto {resultado['metricas']['proyecto']})",
                    resultado, transcripcion, ahora))
        ruta = escribir_evidencia("comparativa-estrategias.md", tabla_comparativa(filas, ahora))
        BITACORA.log(f"\n✓ Comparativa escrita en {ruta}")
        return

    estrategia = EstrategiaResolucion(args.estrategia)
    resultado = escenario.ejecutar(
        args.proyecto, estrategia, args.semilla, mediador,
        max_rondas=min(args.rondas, 3), incluir_codigo=args.codigo)
    transcripcion = BITACORA.volcado()
    BITACORA.log("")
    BITACORA.log(resultado["reportes"]["comunicacion"])
    BITACORA.log(resultado["reportes"]["conflictos"])
    BITACORA.log("")
    BITACORA.log(formato_metricas(resultado["metricas"]))

    m = resultado["metricas"]
    ruta_informe = escribir_evidencia(f"informe-{slug(m['proyecto'])}.md",
                                      resultado["decisiones"]["informe"])
    ruta_corrida = escribir_evidencia(
        f"corrida-{estrategia.value}-seed{args.semilla}.md",
        documento_corrida(
            f"Corrida — estrategia {estrategia.value} · proyecto {m['proyecto']} · semilla {args.semilla}",
            resultado, transcripcion, ahora))
    BITACORA.log(f"\n✓ Informe escrito en {ruta_informe}")
    BITACORA.log(f"✓ Evidencia escrita en {ruta_corrida}")


if __name__ == "__main__":
    main()
