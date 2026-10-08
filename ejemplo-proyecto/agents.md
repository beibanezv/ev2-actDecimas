# agents.md — notas de trabajo de Biblioteca CLI

- Decisión: persistencia en JSON plano antes que SQLite, para no añadir
  dependencias a un ejemplo mínimo (2026-10-08).
- Pendiente: validar duplicados por título y soportar préstamos parciales.
- Pruebas: 3/3 con `unittest`; no hay integración ni CI configurada.
