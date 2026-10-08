# Comparativa de estrategias de resolución (semilla 42)

Generado: 2026-10-08 17:09.
Corridas deterministas (sin mediador LLM) para aislar el efecto de la estrategia.

| Estrategia | Mensajes | Conflictos | Resueltos | Rondas negociación | `acceso_base_datos` → | `revision_con_profesor` → | Segundos |
|---|---|---|---|---|---|---|---|
| prioridad | 32 | 5 | 5 | 0 | Analista | Analista | 0.001 |
| negociacion | 32 | 5 | 5 | 14 | Analista | Investigador | 0.002 |
| arbitraje | 32 | 5 | 5 | 0 | Analista | Investigador | 0.002 |
| votacion | 32 | 5 | 5 | 0 | Investigador | Investigador | 0.001 |
| compromiso | 33 | 5 | 5 | 0 | compartido | compartido | 0.002 |
| primero_en_llegada | 32 | 5 | 5 | 0 | Investigador | Investigador | 0.001 |

**Lectura:** el número de mensajes y conflictos es idéntico entre estrategias (el escenario no cambia); lo que cambia es *quién* obtiene cada recurso y cuántas rondas consume la negociación. La negociación es la única estrategia que gasta rondas (2-3 por conflicto) y la única que puede repartir el acceso cuando los deadlines son asimétricos.
