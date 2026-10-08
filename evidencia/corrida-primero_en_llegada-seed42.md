# Corrida — estrategia primero_en_llegada (proyecto ejemplo-proyecto)

Generado: 2026-10-08 19:50 · equipo LLM: sin equipo LLM

## Transcripción de la simulación

```text
========================================================================
EQUIPO QUE PRODUCE UN ENTREGABLE · proyecto=ejemplo-proyecto · estrategia=primero_en_llegada · semilla=42
Equipo LLM: ninguno (corrida determinista)
Tope de rondas de revisión: 3
========================================================================

[Fase 1] El Coordinador recibe la solicitud y divide el informe
  [mail] coord → ana (propuesta): Tarea 'Informe técnico de ejemplo-proyecto' con 4 subtareas
  [mail] coord → ana (consulta): ¿A qué secciones se postulan?
  [mail] coord → red (propuesta): Tarea 'Informe técnico de ejemplo-proyecto' con 4 subtareas
  [mail] coord → red (consulta): ¿A qué secciones se postulan?
  [mail] coord → rev (propuesta): Tarea 'Informe técnico de ejemplo-proyecto' con 4 subtareas
  [mail] coord → rev (consulta): ¿A qué secciones se postulan?
  ⚠ Conflicto detectado: 2 agentes quieren la misma subtarea 'Resumen ejecutivo': Analista, Redactor
  [conflicto #1 · prioridad] Primero en llegar: Analista solicitó 'Resumen ejecutivo' antes (orden 0) y se lo queda.
  ✓ Resumen ejecutivo → Analista
  ✓ Arquitectura → Redactor
  ✓ Estado y pruebas → Analista
  ✓ Riesgos y pendientes → Revisor

[Fase 2] El Analista lee el proyecto objetivo y extrae el brief
  Material leído: 2 markdown(s), 0 código(s), 4 archivos en el árbol
  Brief (determinista): extraído de títulos y bullets

[Fase 3] El Redactor escribe el borrador v1 con el brief
  Borrador v1: 172 palabras

[Fase 4] El Revisor verifica cada borrador contra la checklist
  ✗ Ronda 1: RECHAZADO — 4 fallo(s) de checklist. la sección 'Resumen ejecutivo' tiene menos de 60 palabras; la sección 'Arquitectura' tiene menos de 60 palabras; la sección 'Estado y pruebas' tiene menos de 60 palabras
  [conflicto #2 · objetivo] Primero en llegar: Redactor solicitó 'informe_v1' antes (orden 1) y se lo queda.
  ⚖ Resolución del conflicto: Primero en llegar: Redactor solicitó 'informe_v1' antes (orden 1) y se lo queda.
  → Se acepta el borrador actual (ganó el Redactor)

[Fase 5] Informe consolidado
  Resumen ejecutivo: Analista
  Arquitectura: Redactor
  Estado y pruebas: Analista
  Riesgos y pendientes: Revisor
  Rondas de revisión usadas: 1/3 · aprobado: False
```

## Reporte de comunicación

```text
REPORTE DE COMUNICACIÓN
Mensajes intercambiados: 23
  aceptacion: 4
  consulta: 3
  informacion: 3
  propuesta: 4
  rechazo: 3
  respuesta: 6
```

## Reporte de conflictos

```text
REPORTE DE CONFLICTOS
Conflictos detectados: 2
Conflictos resueltos: 2/2
  #1 [prioridad] sev 2: 2 agentes quieren la misma subtarea 'Resumen ejecutivo': Analista, Redactor
      → RESUELTO (primero_en_llegada, 0 ronda(s)): Primero en llegar: Analista solicitó 'Resumen ejecutivo' antes (orden 0) y se lo queda.
  #2 [objetivo] sev 3: El Revisor rechaza el borrador v1 (4 fallos de checklist); el Redactor quiere entregarlo.
      → RESUELTO (primero_en_llegada, 0 ronda(s)): Primero en llegar: Redactor solicitó 'informe_v1' antes (orden 1) y se lo queda.
```

## Métricas de la corrida

- **proyecto**: ejemplo-proyecto
- **estrategia**: primero_en_llegada
- **semilla**: 42
- **mediador**: sin equipo LLM
- **mediador_error**: 
- **llamadas_mediador**: 0
- **tokens_mediador_entrada**: 0
- **tokens_mediador_salida**: 0
- **tokens_estimados**: False
- **mensajes**: 23
- **conflictos_detectados**: 2
- **conflictos_resueltos**: 2
- **rondas_negociacion**: 0
- **rondas_revision**: 1
- **aprobado**: False
- **segundos**: 0.005
- **_acciones**: ['aceptar']

## Veredictos del revisor

- Ronda 1: **RECHAZADO** — la sección 'Resumen ejecutivo' tiene menos de 60 palabras; la sección 'Arquitectura' tiene menos de 60 palabras; la sección 'Estado y pruebas' tiene menos de 60 palabras

Aceptado por decisión del equipo antes del tope, con fallos de checklist pendientes.
