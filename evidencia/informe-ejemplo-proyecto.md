## Resumen ejecutivo  
El proyecto **Biblioteca CLI** nace de la necesidad de gestionar de forma sencilla y sin dependencias externas una colección de libros mediante una interfaz de línea de comandos. Su objetivo principal es permitir a usuarios con conocimientos básicos de terminal agregar, prestar y devolver libros, manteniendo la información en un archivo JSON local (`biblioteca.json`). La audiencia prevista son bibliotecarios pequeños, estudiantes y entusiastas de la gestión de datos. Los beneficios incluyen una herramienta ligera, fácil de desplegar y con pruebas unitarias que garantizan la integridad de las operaciones básicas.

## Arquitectura  
La arquitectura se basa en un único módulo `biblioteca.py` que encapsula la lógica de dominio y la interfaz CLI, siguiendo el patrón **Command** para separar la entrada del usuario de la lógica de negocio. La persistencia se realiza mediante la biblioteca estándar `json`, escribiendo y leyendo directamente el archivo `biblioteca.json`. No existen dependencias externas, lo que simplifica la distribución. La estrategia de pruebas utiliza `unittest` en `test_biblioteca.py`, cubriendo las tres operaciones esenciales (agregar, prestar, devolver). La documentación interna se mantiene en `agents.md`, donde se registran decisiones de diseño y notas de trabajo.

## Estado y pruebas  
El proyecto cuenta con **3 pruebas unitarias** que verifican el correcto funcionamiento de las operaciones de agregar, prestar y devolver libros. Todas las pruebas pasan con éxito (3/3) bajo el framework `unittest`. No se ha configurado integración continua ni pruebas de integración, por lo que la cobertura se limita al dominio. El archivo `biblioteca.json` se actualiza de forma síncrona cada vez que se ejecuta una operación, garantizando la consistencia de los datos en disco.

## Riesgos y pendientes  
- **Validación de duplicados por título**: no se detectan libros con el mismo título, lo que puede generar inconsistencias.  
- **Validación de ISBN**: el sistema no verifica la validez ni unicidad del ISBN.  
- **Préstamos parciales**: no se soporta la gestión de múltiples copias de un mismo libro.  
- **Seguridad de datos**: los datos se guardan en texto plano sin cifrado, exponiendo información sensible.  
- **Integración y CI**: no existe configuración de integración continua, lo que dificulta la detección temprana de regresiones.  
- **Gestión de dependencias**: aunque se evita dependencias externas, la falta de un entorno virtual documentado puede generar conflictos de versiones.
