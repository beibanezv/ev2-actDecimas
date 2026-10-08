"""Pruebas de integración: el escenario corre completo y respeta el tope."""

from pathlib import Path

from simulacion.conflictos import EstrategiaResolucion
from simulacion.escenario import (
    RAIZ_EJEMPLO,
    checklist_determinista,
    ejecutar,
    leer_proyecto,
    secciones_del_texto,
)

RAIZ = Path(__file__).resolve().parents[1]


def test_escenario_completo_determinista():
    r = ejecutar(RAIZ_EJEMPLO, EstrategiaResolucion.NEGOCIACION, semilla=42, mediador=None)
    d, m = r["decisiones"], r["metricas"]
    assert d["proyecto"] == Path(RAIZ_EJEMPLO).name
    secciones = secciones_del_texto(d["informe"])
    exigidas = {"Resumen ejecutivo", "Arquitectura",
                "Estado y pruebas", "Riesgos y pendientes"}
    assert exigidas <= set(secciones)
    assert d["secciones"] and all(v for v in d["secciones"].values())
    assert m["mensajes"] > 0
    assert m["conflictos_detectados"] >= 2      # reparto (prioridad) + revisión (objetivo)
    assert m["conflictos_resueltos"] == m["conflictos_detectados"]
    assert m["tokens_mediador_salida"] == 0     # sin equipo LLM
    assert m["rondas_revision"] <= 3            # tope duro (error #6)


def test_misma_semilla_produce_el_mismo_informe():
    a = ejecutar(RAIZ_EJEMPLO, EstrategiaResolucion.VOTACION, 42, None)["decisiones"]
    b = ejecutar(RAIZ_EJEMPLO, EstrategiaResolucion.VOTACION, 42, None)["decisiones"]
    assert a["informe"] == b["informe"]
    assert a["veredictos"] == b["veredictos"]


def test_checklist_detecta_placeholder_y_archivos_inventados():
    material = leer_proyecto(RAIZ_EJEMPLO)
    texto = ("## Resumen ejecutivo\n\nTODO completar.\n\n"
             "## Arquitectura\n\nSe apoya en modulo_inexistente.py y datos secretos.\n\n"
             "## Estado y pruebas\n\nSin datos.\n\n"
             "## Riesgos y pendientes\n\nlorem ipsum dolor sit.")
    c = checklist_determinista(texto, {"archivos_citados": []}, material)
    assert not c["aprobado"]
    descripciones = " ".join(f["descripcion"] for f in c["fallos"])
    assert "placeholder" in descripciones
    assert "no verificables" in descripciones


def test_checklist_aprueba_un_informe_completo_y_verificable():
    material = leer_proyecto(RAIZ_EJEMPLO)
    palabras = " ".join(["dato"] * 70)
    texto = ("## Resumen ejecutivo\n\n" + palabras + "\n\n"
             "## Arquitectura\n\n" + palabras + "\n\n"
             "## Estado y pruebas\n\n" + palabras + "\n\n"
             "## Riesgos y pendientes\n\n" + palabras)
    # cita archivos reales del material leído
    citados = sorted(Path(k).name for k in material["md"])[:2]
    texto += f"\n\nArchivos revisados: {', '.join(citados)}."
    c = checklist_determinista(texto, {"archivos_citados": citados}, material)
    assert c["aprobado"], c["fallos"]


def test_tope_de_rondas_se_respeta_y_el_arbitro_cierra():
    # El redactor determinista nunca llega a 60 palabras por sección → el
    # revisor rechaza siempre; el laudo del árbitro debe cerrar en el tope.
    r = ejecutar(RAIZ_EJEMPLO, EstrategiaResolucion.NEGOCIACION, 42, None)
    assert r["metricas"]["rondas_revision"] == 3
    assert "Resolución final" in r["decisiones"]["informe"]
    assert "LAUDO" in r["decisiones"]["informe"]


def test_estrategia_que_deja_ganar_al_revisor_corrige_todo():
    # El Revisor es el gate de calidad (prioridad 1): con PRIORIDAD o ARBITRAJE
    # gana el revisor y el Redactor debe corregir todos los puntos.
    r = ejecutar(RAIZ_EJEMPLO, EstrategiaResolucion.PRIORIDAD, 42, None)
    assert "corregir_todo" in r["decisiones"]["acciones"]


def test_primero_en_llegar_deja_ganar_al_redactor_y_acepta_antes():
    # En el conflicto redactor/revisor el Redactor llegó primero (orden 1
    # frente a 2): la estrategia primero-en-llegada acepta el borrador.
    r = ejecutar(RAIZ_EJEMPLO, EstrategiaResolucion.PRIMERO_EN_LLEGADA, 42, None)
    assert "aceptar" in r["decisiones"]["acciones"]
    assert r["metricas"]["rondas_revision"] < 3


def test_leer_proyecto_ignora_git_y_opta_por_md():
    material = leer_proyecto(RAIZ_EJEMPLO)  # sin --codigo
    assert "README.md" in material["md"] and "agents.md" in material["md"]
    assert material["codigo"] == {}
    assert "biblioteca.py" in material["arbol"]  # el árbol sí lista todo
    con_codigo = leer_proyecto(RAIZ_EJEMPLO, incluir_codigo=True)
    assert "biblioteca.py" in con_codigo["codigo"]
    # tope de caracteres por archivo (error #5: acotar el coste)
    assert all(len(v) <= 2600 for v in con_codigo["md"].values())
