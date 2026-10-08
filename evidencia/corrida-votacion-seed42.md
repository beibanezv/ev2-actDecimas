# Corrida — estrategia votacion (semilla 42)

Generado: 2026-10-08 17:09 · mediador: sin mediador

## Transcripción de la simulación

```text
========================================================================
SISTEMA DE COLABORACIÓN ACADÉMICA · estrategia=votacion · semilla=42
Mediador: ninguno (corrida determinista)
========================================================================

[Fase 1] Reparto de secciones del informe
  [mail] coord → inv (propuesta): Tarea 'Informe académico grupal' con 3 subtareas
  [mail] coord → inv (consulta): ¿Qué sección prefieren? Respondan con su primera opción.
  [mail] coord → ana (propuesta): Tarea 'Informe académico grupal' con 3 subtareas
  [mail] coord → ana (consulta): ¿Qué sección prefieren? Respondan con su primera opción.
  [mail] coord → red (propuesta): Tarea 'Informe académico grupal' con 3 subtareas
  [mail] coord → red (consulta): ¿Qué sección prefieren? Respondan con su primera opción.
  ✓ Revisión bibliográfica → Investigador (asignado por capacidad)
  ✓ Análisis de datos → Analista
  ⚠ Conflicto detectado: 2 agentes quieren la misma subtarea 'redaccion_informe': Investigador, Redactor
  [conflicto #1 · prioridad] Por votación (Investigador: 2) gana Investigador para 'redaccion_informe'.

[Fase 2] Votación del tema del informe (3 opciones)
  🗳 Investigador vota por «Riesgos de sesgo en modelos de lenguaje educativos»
  🗳 Analista vota por «Impacto de los agentes de IA en la evaluación formativa»
  🗳 Redactor vota por «Tutores LLM en educación media: oportunidades y límites»
  Conteo: {'Impacto de los agentes de IA en la evaluación formativa': 1, 'Riesgos de sesgo en modelos de lenguaje educativos': 1, 'Tutores LLM en educación media: oportunidades y límites': 1}
  [conflicto #2 · objetivo] Por votación (Redactor: 1, Analista: 1, Investigador: 1) gana Investigador para 'tema_del_informe'.
  ⚖ Empate resuelto → «Riesgos de sesgo en modelos de lenguaje educativos»

[Fase 3] Asignación de recursos exclusivos
  [mail] coord → inv (consulta): Voten por el tema del informe.
  [mail] coord → ana (consulta): Voten por el tema del informe.
  [mail] coord → red (consulta): Voten por el tema del informe.
  ⚠ Conflicto detectado: 2 agentes solicitan el recurso exclusivo 'acceso_base_datos': Investigador, Analista
  [conflicto #3 · recurso] Por votación (Investigador: 2) gana Investigador para 'acceso_base_datos'.
  ⚠ Conflicto detectado: 2 agentes solicitan el recurso exclusivo 'sala_de_trabajo': Analista, Redactor
  [conflicto #4 · recurso] Por votación (Analista: 2) gana Analista para 'sala_de_trabajo'.

[Fase 4] Conflicto temporal: slot de revisión con el profesor
  ⚠ Conflicto detectado: 2 agentes compiten por el slot 'revision_con_profesor' (capacidad 1): Investigador (deadline semana 3), Analista (deadline semana 5)
  [conflicto #5 · temporal] Por votación (Analista: 1, Investigador: 1) gana Investigador para 'revision_con_profesor'.

[Fase 5] Plan consolidado
  Tema: Riesgos de sesgo en modelos de lenguaje educativos
  Revisión bibliográfica: Investigador
  Análisis de datos: Analista
  Redacción del informe: Investigador
  Investigador obtiene: redaccion_informe, tema_del_informe, acceso_base_datos, revision_con_profesor (deadline semana 3)
  Analista obtiene: sala_de_trabajo (deadline semana 5)
```

## Reporte de comunicación

```text
REPORTE DE COMUNICACIÓN
Mensajes intercambiados: 32
  aceptacion: 3
  consulta: 6
  peticion: 8
  propuesta: 3
  rechazo: 3
  respuesta: 9
```

## Reporte de conflictos

```text
REPORTE DE CONFLICTOS
Conflictos detectados: 5
Conflictos resueltos: 5/5
  #1 [prioridad] sev 2: 2 agentes quieren la misma subtarea 'redaccion_informe': Investigador, Redactor
      → RESUELTO (votacion, 0 ronda(s)): Por votación (Investigador: 2) gana Investigador para 'redaccion_informe'.
  #2 [objetivo] sev 2: La votación empató entre 3 temas: Impacto de los agentes de IA en la evaluación formativa; Riesgos de sesgo en modelos de lenguaje educativos; Tutores LLM en educación media: oportunidades y límites
      → RESUELTO (votacion, 0 ronda(s)): Por votación (Redactor: 1, Analista: 1, Investigador: 1) gana Investigador para 'tema_del_informe'.
  #3 [recurso] sev 3: 2 agentes solicitan el recurso exclusivo 'acceso_base_datos': Investigador, Analista
      → RESUELTO (votacion, 0 ronda(s)): Por votación (Investigador: 2) gana Investigador para 'acceso_base_datos'.
  #4 [recurso] sev 3: 2 agentes solicitan el recurso exclusivo 'sala_de_trabajo': Analista, Redactor
      → RESUELTO (votacion, 0 ronda(s)): Por votación (Analista: 2) gana Analista para 'sala_de_trabajo'.
  #5 [temporal] sev 2: 2 agentes compiten por el slot 'revision_con_profesor' (capacidad 1): Investigador (deadline semana 3), Analista (deadline semana 5)
      → RESUELTO (votacion, 0 ronda(s)): Por votación (Analista: 1, Investigador: 1) gana Investigador para 'revision_con_profesor'.
```

## Métricas de la corrida

- **estrategia**: votacion
- **semilla**: 42
- **mediador**: sin mediador
- **llamadas_mediador**: 0
- **tokens_mediador_entrada**: 0
- **tokens_mediador_salida**: 0
- **tokens_estimados**: False
- **mensajes**: 32
- **conflictos_detectados**: 5
- **conflictos_resueltos**: 5
- **rondas_negociacion**: 0
- **segundos**: 0.001
- **asignaciones**: {'redaccion_informe': 'Investigador', 'tema_del_informe': 'Investigador', 'acceso_base_datos': 'Investigador', 'sala_de_trabajo': 'Analista', 'revision_con_profesor': 'Investigador'}

## Acta

# Acta de constitución del equipo (generada sin LLM)

## Tema aprobado
Riesgos de sesgo en modelos de lenguaje educativos

## Equipo y secciones
- **Revisión bibliográfica**: Investigador
- **Análisis de datos**: Analista
- **Redacción del informe**: Investigador

## Recursos asignados
- **Investigador**: redaccion_informe, tema_del_informe, acceso_base_datos, revision_con_profesor
- **Analista**: sala_de_trabajo

## Conflictos y resoluciones
- Conflicto #1 (prioridad sobre «redaccion_informe»): Por votación (Investigador: 2) gana Investigador para 'redaccion_informe'.
- Conflicto #2 (objetivo sobre «tema_del_informe»): Por votación (Redactor: 1, Analista: 1, Investigador: 1) gana Investigador para 'tema_del_informe'.
- Conflicto #3 (recurso sobre «acceso_base_datos»): Por votación (Investigador: 2) gana Investigador para 'acceso_base_datos'.
- Conflicto #4 (recurso sobre «sala_de_trabajo»): Por votación (Analista: 2) gana Analista para 'sala_de_trabajo'.
- Conflicto #5 (temporal sobre «revision_con_profesor»): Por votación (Analista: 1, Investigador: 1) gana Investigador para 'revision_con_profesor'.

## Acuerdos
- Cada sección tiene responsable definido y plazo asociado a su deadline.
- Los conflictos se resolvieron con la estrategia configurada y quedan trazados.

