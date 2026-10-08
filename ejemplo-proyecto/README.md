# Biblioteca CLI

Mini aplicación de consola para gestionar una biblioteca personal: registrar
libros, prestarlos y devolverlos. Sirve como **proyecto de ejemplo** para la
demo del sistema multi-agente (`python main.py --proyecto ejemplo-proyecto`).

## Stack

- Python 3.11 o superior.
- **Sin dependencias externas** (solo biblioteca estándar).
- Persistencia en un archivo JSON local (`biblioteca.json`).

## Instalación

No requiere instalación. Clona el repo y ejecuta:

```bash
python biblioteca.py
```

## Uso

```bash
python biblioteca.py agregar "Cien años de soledad" "García Márquez"
python biblioteca.py prestar 1 "Ana"
python biblioteca.py devolver 1
python biblioteca.py listar
```

## Estructura

- `biblioteca.py` — lógica de dominio y CLI (un solo archivo).
- `test_biblioteca.py` — pruebas del dominio con `unittest`.
- `agents.md` — notas de trabajo del proyecto.

## Estado

- 3 pruebas pasan (`python test_biblioteca.py`) y cubren agregar, prestar y
  devolver.
- La CLI no valida ISBN ni duplicados: un mismo título puede registrarse dos
  veces.
- Los datos se guardan en texto plano, sin cifrado.
