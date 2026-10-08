# Corrida — estrategia compromiso (semilla 42)

Generado: 2026-10-08 17:09 · mediador: sin mediador

## Transcripción de la simulación

```text
========================================================================
SISTEMA DE COLABORACIÓN ACADÉMICA · estrategia=compromiso · semilla=42
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
  [conflicto #1 · prioridad] Compromiso: 'redaccion_informe' se divide en 2 partes iguales (50% cada una) entre Investigador, Redactor.

[Fase 2] Votación del tema del informe (3 opciones)
  🗳 Investigador vota por «Riesgos de sesgo en modelos de lenguaje educativos»
  🗳 Analista vota por «Impacto de los agentes de IA en la evaluación formativa»
  🗳 Redactor vota por «Tutores LLM en educación media: oportunidades y límites»
  Conteo: {'Impacto de los agentes de IA en la evaluación formativa': 1, 'Riesgos de sesgo en modelos de lenguaje educativos': 1, 'Tutores LLM en educación media: oportunidades y límites': 1}
  [conflicto #2 · objetivo] Compromiso: 'tema_del_informe' se divide en 3 partes iguales (33% cada una) entre Investigador, Analista, Redactor.
  ⚖ Empate resuelto → «Impacto de los agentes de IA en la evaluación formativa»

[Fase 3] Asignación de recursos exclusivos
  [mail] coord → inv (consulta): Voten por el tema del informe.
  [mail] coord → ana (consulta): Voten por el tema del informe.
  [mail] coord → red (consulta): Voten por el tema del informe.
  ⚠ Conflicto detectado: 2 agentes solicitan el recurso exclusivo 'acceso_base_datos': Investigador, Analista
  [conflicto #3 · recurso] Compromiso: 'acceso_base_datos' se divide en 2 partes iguales (50% cada una) entre Investigador, Analista.
  ⚠ Conflicto detectado: 2 agentes solicitan el recurso exclusivo 'sala_de_trabajo': Analista, Redactor
  [conflicto #4 · recurso] Compromiso: 'sala_de_trabajo' se divide en 2 partes iguales (50% cada una) entre Analista, Redactor.

[Fase 4] Conflicto temporal: slot de revisión con el profesor
  ⚠ Conflicto detectado: 2 agentes compiten por el slot 'revision_con_profesor' (capacidad 1): Investigador (deadline semana 3), Analista (deadline semana 5)
  [conflicto #5 · temporal] Compromiso: 'revision_con_profesor' se divide en 2 partes iguales (50% cada una) entre Investigador, Analista.

[Fase 5] Plan consolidado
  Tema: Impacto de los agentes de IA en la evaluación formativa
  Revisión bibliográfica: Investigador
  Análisis de datos: Analista
  Redacción del informe: Investigador, Redactor
```

## Reporte de comunicación

```text
REPORTE DE COMUNICACIÓN
Mensajes intercambiados: 33
  aceptacion: 4
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
      → RESUELTO (compromiso, 0 ronda(s)): Compromiso: 'redaccion_informe' se divide en 2 partes iguales (50% cada una) entre Investigador, Redactor.
  #2 [objetivo] sev 2: La votación empató entre 3 temas: Impacto de los agentes de IA en la evaluación formativa; Riesgos de sesgo en modelos de lenguaje educativos; Tutores LLM en educación media: oportunidades y límites
      → RESUELTO (compromiso, 0 ronda(s)): Compromiso: 'tema_del_informe' se divide en 3 partes iguales (33% cada una) entre Investigador, Analista, Redactor.
  #3 [recurso] sev 3: 2 agentes solicitan el recurso exclusivo 'acceso_base_datos': Investigador, Analista
      → RESUELTO (compromiso, 0 ronda(s)): Compromiso: 'acceso_base_datos' se divide en 2 partes iguales (50% cada una) entre Investigador, Analista.
  #4 [recurso] sev 3: 2 agentes solicitan el recurso exclusivo 'sala_de_trabajo': Analista, Redactor
      → RESUELTO (compromiso, 0 ronda(s)): Compromiso: 'sala_de_trabajo' se divide en 2 partes iguales (50% cada una) entre Analista, Redactor.
  #5 [temporal] sev 2: 2 agentes compiten por el slot 'revision_con_profesor' (capacidad 1): Investigador (deadline semana 3), Analista (deadline semana 5)
      → RESUELTO (compromiso, 0 ronda(s)): Compromiso: 'revision_con_profesor' se divide en 2 partes iguales (50% cada una) entre Investigador, Analista.
```

## Métricas de la corrida

- **estrategia**: compromiso
- **semilla**: 42
- **mediador**: sin mediador
- **llamadas_mediador**: 0
- **tokens_mediador_entrada**: 0
- **tokens_mediador_salida**: 0
- **tokens_estimados**: False
- **mensajes**: 33
- **conflictos_detectados**: 5
- **conflictos_resueltos**: 5
- **rondas_negociacion**: 0
- **segundos**: 0.002
- **asignaciones**: {'redaccion_informe': 'compartido', 'tema_del_informe': 'compartido', 'acceso_base_datos': 'compartido', 'sala_de_trabajo': 'compartido', 'revision_con_profesor': 'compartido'}

## Acta

# Acta de constitución del equipo (generada sin LLM)

## Tema aprobado
Impacto de los agentes de IA en la evaluación formativa

## Equipo y secciones
- **Revisión bibliográfica**: Investigador
- **Análisis de datos**: Analista
- **Redacción del informe**: Investigador, Redactor

## Recursos asignados
- (sin recursos exclusivos asignados)

## Conflictos y resoluciones
- Conflicto #1 (prioridad sobre «redaccion_informe»): Compromiso: 'redaccion_informe' se divide en 2 partes iguales (50% cada una) entre Investigador, Redactor.
- Conflicto #2 (objetivo sobre «tema_del_informe»): Compromiso: 'tema_del_informe' se divide en 3 partes iguales (33% cada una) entre Investigador, Analista, Redactor.
- Conflicto #3 (recurso sobre «acceso_base_datos»): Compromiso: 'acceso_base_datos' se divide en 2 partes iguales (50% cada una) entre Investigador, Analista.
- Conflicto #4 (recurso sobre «sala_de_trabajo»): Compromiso: 'sala_de_trabajo' se divide en 2 partes iguales (50% cada una) entre Analista, Redactor.
- Conflicto #5 (temporal sobre «revision_con_profesor»): Compromiso: 'revision_con_profesor' se divide en 2 partes iguales (50% cada una) entre Investigador, Analista.

## Acuerdos
- Cada sección tiene responsable definido y plazo asociado a su deadline.
- Los conflictos se resolvieron con la estrategia configurada y quedan trazados.

