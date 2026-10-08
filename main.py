"""CLI del Sistema de Colaboración Académica (actividad de décimas IL2.3).

Ejemplos::

    python main.py --estrategia negociacion --seed 42   # corrida completa con mediador LLM
    python main.py --estrategia compromiso --llm no     # corrida determinista, sin red
    python main.py --comparar                           # tabla de las 6 estrategias
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from simulacion import escenario
from simulacion.bitacora import BITACORA
from simulacion.conflictos import EstrategiaResolucion
from simulacion.mediador_llm import MODELO_POR_DEFECTO, MediadorLLM

RAIZ = Path(__file__).resolve().parent
CARPETA_EVIDENCIA = RAIZ / "evidencia"


def formato_metricas(m: dict) -> str:
    lineas = ["## Métricas de la corrida", ""]
    for k, v in m.items():
        lineas.append(f"- **{k}**: {v}")
    return "\n".join(lineas)


def tabla_comparativa(filas: list[dict], semilla: int, ahora: str) -> str:
    lineas = [
        f"# Comparativa de estrategias de resolución (semilla {semilla})",
        "",
        f"Generado: {ahora}.",
        "Corridas deterministas (sin mediador LLM) para aislar el efecto de la estrategia.",
        "",
        "| Estrategia | Mensajes | Conflictos | Resueltos | Rondas negociación | "
        "`acceso_base_datos` → | `revision_con_profesor` → | Segundos |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for m in filas:
        a = m["asignaciones"]
        lineas.append(
            f"| {m['estrategia']} | {m['mensajes']} | {m['conflictos_detectados']} | "
            f"{m['conflictos_resueltos']} | {m['rondas_negociacion']} | "
            f"{a.get('acceso_base_datos', '—')} | {a.get('revision_con_profesor', '—')} | "
            f"{m['segundos']} |"
        )
    lineas += [
        "",
        "**Lectura:** el número de mensajes y conflictos es idéntico entre estrategias "
        "(el escenario no cambia); lo que cambia es *quién* obtiene cada recurso y "
        "cuántas rondas consume la negociación. La negociación es la única estrategia "
        "que gasta rondas (2-3 por conflicto) y la única que puede repartir el acceso "
        "cuando los deadlines son asimétricos.",
        "",
    ]
    return "\n".join(lineas)


def escribir_evidencia(nombre: str, contenido: str) -> Path:
    CARPETA_EVIDENCIA.mkdir(exist_ok=True)
    ruta = CARPETA_EVIDENCIA / nombre
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def documento_corrida(titulo: str, resultado: dict, ahora: str) -> str:
    m = resultado["metricas"]
    return "\n".join([
        f"# {titulo}",
        "",
        f"Generado: {ahora} · mediador: {m['mediador']}",
        "",
        "## Transcripción de la simulación",
        "",
        "```text",
        resultado["transcripcion"],
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
        "## Acta",
        "",
        resultado["acta"],
        "",
    ])


def main() -> None:
    try:  # consola en UTF-8 cuando se puede (Windows usa cp1252 por defecto)
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Sistema de Colaboración Académica (IL2.3)")
    parser.add_argument("--estrategia", default="negociacion",
                        choices=[e.value for e in EstrategiaResolucion])
    parser.add_argument("--seed", "--semilla", dest="semilla", type=int, default=42,
                        help="semilla del generador aleatorio (reproducibilidad)")
    parser.add_argument("--llm", choices=["auto", "si", "no"], default="auto",
                        help="auto/si: usa ChatGroq si hay clave; no: determinsta puro")
    parser.add_argument("--modelo", default=MODELO_POR_DEFECTO)
    parser.add_argument("--comparar", action="store_true",
                        help="corre las 6 estrategias con la misma semilla y escribe la comparativa")
    args = parser.parse_args()

    mediador = MediadorLLM(modelo=args.modelo, activo=args.llm != "no")
    if args.llm == "no":
        BITACORA.log("Mediador LLM desactivado (--llm no): corrida determinista.")
    elif not mediador.disponible:
        BITACORA.log(f"Mediador LLM no disponible ({mediador.motivo_fallback}); "
                     "se usa el mediador determinista.")
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    if args.comparar:
        filas: list[dict] = []
        for e in EstrategiaResolucion:
            resultado = escenario.ejecutar(e, args.semilla, mediador=None)
            resultado["transcripcion"] = BITACORA.volcado()
            BITACORA.limpiar()
            filas.append(resultado["metricas"])
            escribir_evidencia(
                f"corrida-{e.value}-seed{args.semilla}.md",
                documento_corrida(f"Corrida — estrategia {e.value} (semilla {args.semilla})",
                                  resultado, ahora))
        ruta = escribir_evidencia("comparativa-estrategias.md",
                                  tabla_comparativa(filas, args.semilla, ahora))
        BITACORA.log(f"\n✓ Comparativa escrita en {ruta}")
        return

    estrategia = EstrategiaResolucion(args.estrategia)
    resultado = escenario.ejecutar(estrategia, args.semilla, mediador)
    resultado["transcripcion"] = BITACORA.volcado()
    BITACORA.log("")
    BITACORA.log(resultado["reportes"]["comunicacion"])
    BITACORA.log(resultado["reportes"]["conflictos"])
    BITACORA.log("")
    BITACORA.log(formato_metricas(resultado["metricas"]))
    ruta = escribir_evidencia(
        f"corrida-{estrategia.value}-seed{args.semilla}.md",
        documento_corrida(f"Corrida — estrategia {estrategia.value} (semilla {args.semilla})",
                          resultado, ahora))
    BITACORA.log(f"\n✓ Evidencia escrita en {ruta}")


if __name__ == "__main__":
    main()
