# Corrida — estrategia negociacion (semilla 42)

Generado: 2026-10-08 17:09 · mediador: sin mediador

## Transcripción de la simulación

```text
========================================================================
SISTEMA DE COLABORACIÓN ACADÉMICA · estrategia=negociacion · semilla=42
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
    [negociación] Ronda 1/3 — mediador determinista: el agente con mayor prioridad conserva el acceso y el otro acepta el segundo turno
    [negociación] Ronda 2/3 — mediador determinista: reparto 50/50 del acceso (o de la carga asociada al recurso)
    [negociación] Ronda 3/3 — mediador determinista: arbitraje forzado: gana el agente con el deadline más próximo
  [conflicto #1 · prioridad] Arbitraje (acuerdo forzado por tope de 3 rondas): Investigador obtiene 'redaccion_informe'.

[Fase 2] Votación del tema del informe (3 opciones)
  🗳 Investigador vota por «Riesgos de sesgo en modelos de lenguaje educativos»
  🗳 Analista vota por «Impacto de los agentes de IA en la evaluación formativa»
  🗳 Redactor vota por «Tutores LLM en educación media: oportunidades y límites»
  Conteo: {'Impacto de los agentes de IA en la evaluación formativa': 1, 'Riesgos de sesgo en modelos de lenguaje educativos': 1, 'Tutores LLM en educación media: oportunidades y límites': 1}
    [negociación] Ronda 1/3 — mediador determinista: el agente con mayor prioridad conserva el acceso y el otro acepta el segundo turno
    [negociación] Ronda 2/3 — mediador determinista: reparto 50/50 del acceso (o de la carga asociada al recurso)
    [negociación] Ronda 3/3 — mediador determinista: arbitraje forzado: gana el agente con el deadline más próximo
  [conflicto #2 · objetivo] Arbitraje (acuerdo forzado por tope de 3 rondas): Analista obtiene 'tema_del_informe'.
  ⚖ Empate resuelto → «Impacto de los agentes de IA en la evaluación formativa»

[Fase 3] Asignación de recursos exclusivos
  [mail] coord → inv (consulta): Voten por el tema del informe.
  [mail] coord → ana (consulta): Voten por el tema del informe.
  [mail] coord → red (consulta): Voten por el tema del informe.
  ⚠ Conflicto detectado: 2 agentes solicitan el recurso exclusivo 'acceso_base_datos': Investigador, Analista
    [negociación] Ronda 1/3 — mediador determinista: el agente con mayor prioridad conserva el acceso y el otro acepta el segundo turno
    [negociación] Ronda 2/3 — mediador determinista: reparto 50/50 del acceso (o de la carga asociada al recurso)
    [negociación] Ronda 3/3 — mediador determinista: arbitraje forzado: gana el agente con el deadline más próximo
  [conflicto #3 · recurso] Arbitraje (acuerdo forzado por tope de 3 rondas): Analista obtiene 'acceso_base_datos'.
  ⚠ Conflicto detectado: 2 agentes solicitan el recurso exclusivo 'sala_de_trabajo': Analista, Redactor
    [negociación] Ronda 1/3 — mediador determinista: el agente con mayor prioridad conserva el acceso y el otro acepta el segundo turno
    [negociación] Ronda 2/3 — mediador determinista: reparto 50/50 del acceso (o de la carga asociada al recurso)
  [conflicto #4 · recurso] Compromiso: 'sala_de_trabajo' se divide en 2 partes iguales (50% cada una) entre Analista, Redactor. (acuerdo en ronda 2: urgencia levemente asimétrica)

[Fase 4] Conflicto temporal: slot de revisión con el profesor
  ⚠ Conflicto detectado: 2 agentes compiten por el slot 'revision_con_profesor' (capacidad 1): Investigador (deadline semana 3), Analista (deadline semana 5)
    [negociación] Ronda 1/3 — mediador determinista: el agente con mayor prioridad conserva el acceso y el otro acepta el segundo turno
    [negociación] Ronda 2/3 — mediador determinista: reparto 50/50 del acceso (o de la carga asociada al recurso)
    [negociación] Ronda 3/3 — mediador determinista: arbitraje forzado: gana el agente con el deadline más próximo
  [conflicto #5 · temporal] Arbitraje (acuerdo forzado por tope de 3 rondas): Investigador obtiene 'revision_con_profesor'.

[Fase 5] Plan consolidado
  Tema: Impacto de los agentes de IA en la evaluación formativa
  Revisión bibliográfica: Investigador
  Análisis de datos: Analista
  Redacción del informe: Investigador
  Investigador obtiene: redaccion_informe, revision_con_profesor (deadline semana 3)
  Analista obtiene: tema_del_informe, acceso_base_datos (deadline semana 5)
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
      → RESUELTO (negociacion, 3 ronda(s)): Arbitraje (acuerdo forzado por tope de 3 rondas): Investigador obtiene 'redaccion_informe'.
  #2 [objetivo] sev 2: La votación empató entre 3 temas: Impacto de los agentes de IA en la evaluación formativa; Riesgos de sesgo en modelos de lenguaje educativos; Tutores LLM en educación media: oportunidades y límites
      → RESUELTO (negociacion, 3 ronda(s)): Arbitraje (acuerdo forzado por tope de 3 rondas): Analista obtiene 'tema_del_informe'.
  #3 [recurso] sev 3: 2 agentes solicitan el recurso exclusivo 'acceso_base_datos': Investigador, Analista
      → RESUELTO (negociacion, 3 ronda(s)): Arbitraje (acuerdo forzado por tope de 3 rondas): Analista obtiene 'acceso_base_datos'.
  #4 [recurso] sev 3: 2 agentes solicitan el recurso exclusivo 'sala_de_trabajo': Analista, Redactor
      → RESUELTO (negociacion, 2 ronda(s)): Compromiso: 'sala_de_trabajo' se divide en 2 partes iguales (50% cada una) entre Analista, Redactor. (acuerdo en ronda 2: urgencia levemente asimétrica)
  #5 [temporal] sev 2: 2 agentes compiten por el slot 'revision_con_profesor' (capacidad 1): Investigador (deadline semana 3), Analista (deadline semana 5)
      → RESUELTO (negociacion, 3 ronda(s)): Arbitraje (acuerdo forzado por tope de 3 rondas): Investigador obtiene 'revision_con_profesor'.
```

## Métricas de la corrida

- **estrategia**: negociacion
- **semilla**: 42
- **mediador**: sin mediador
- **llamadas_mediador**: 0
- **tokens_mediador_entrada**: 0
- **tokens_mediador_salida**: 0
- **tokens_estimados**: False
- **mensajes**: 32
- **conflictos_detectados**: 5
- **conflictos_resueltos**: 5
- **rondas_negociacion**: 14
- **segundos**: 0.002
- **asignaciones**: {'redaccion_informe': 'Investigador', 'tema_del_informe': 'Analista', 'acceso_base_datos': 'Analista', 'sala_de_trabajo': 'compartido', 'revision_con_profesor': 'Investigador'}

## Acta

# Acta de constitución del equipo (generada sin LLM)

## Tema aprobado
Impacto de los agentes de IA en la evaluación formativa

## Equipo y secciones
- **Revisión bibliográfica**: Investigador
- **Análisis de datos**: Analista
- **Redacción del informe**: Investigador

## Recursos asignados
- **Investigador**: redaccion_informe, revision_con_profesor
- **Analista**: tema_del_informe, acceso_base_datos

## Conflictos y resoluciones
- Conflicto #1 (prioridad sobre «redaccion_informe»): Arbitraje (acuerdo forzado por tope de 3 rondas): Investigador obtiene 'redaccion_informe'.
- Conflicto #2 (objetivo sobre «tema_del_informe»): Arbitraje (acuerdo forzado por tope de 3 rondas): Analista obtiene 'tema_del_informe'.
- Conflicto #3 (recurso sobre «acceso_base_datos»): Arbitraje (acuerdo forzado por tope de 3 rondas): Analista obtiene 'acceso_base_datos'.
- Conflicto #4 (recurso sobre «sala_de_trabajo»): Compromiso: 'sala_de_trabajo' se divide en 2 partes iguales (50% cada una) entre Analista, Redactor. (acuerdo en ronda 2: urgencia levemente asimétrica)
- Conflicto #5 (temporal sobre «revision_con_profesor»): Arbitraje (acuerdo forzado por tope de 3 rondas): Investigador obtiene 'revision_con_profesor'.

## Acuerdos
- Cada sección tiene responsable definido y plazo asociado a su deadline.
- Los conflictos se resolvieron con la estrategia configurada y quedan trazados.

