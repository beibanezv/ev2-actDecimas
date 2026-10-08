# Comparativa de estrategias de resolución del desacuerdo

Generado: 2026-10-08 19:50. Corridas deterministas (sin equipo LLM) para aislar el efecto de la estrategia sobre el MISMO informe borrador.

| Estrategia | Rondas revisión | Aprobado | Acciones del revisor | Conflictos | Rondas neg. | Segundos |
|---|---|---|---|---|---|---|
| prioridad | 3 | no | corregir_todo, corregir_todo, corregir_todo | 4/4 | 0 | 0.008 |
| negociacion | 3 | no | corregir_mitad, corregir_mitad, corregir_mitad | 4/4 | 7 | 0.016 |
| arbitraje | 3 | no | corregir_todo, corregir_todo, corregir_todo | 4/4 | 0 | 0.007 |
| votacion | 1 | no | aceptar | 2/2 | 0 | 0.006 |
| compromiso | 3 | no | corregir_mitad, corregir_mitad, corregir_mitad | 4/4 | 0 | 0.009 |
| primero_en_llegada | 1 | no | aceptar | 2/2 | 0 | 0.005 |

**Lectura:** el escenario y el borrador son idénticos entre estrategias; lo que cambia es la acción que toma el equipo cuando el revisor rechaza. El Revisor es el gate de calidad (prioridad 1): las estrategias por prioridad y arbitraje le dan la razón y el Redactor corrige TODO hasta agotar el tope de 3 rondas; el compromiso y la negociación corrigen la mitad de los puntos; primero-en-llegada deja ganar al Redactor (llegó primero) y acepta el borrador con fallos; la votación depende del sorteo con semilla. Ninguna estrategia cambia los hechos: decide quién impone su criterio y cuántas rondas cuesta.
