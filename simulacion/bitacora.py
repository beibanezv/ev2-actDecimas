"""Bitácora: imprime en consola y guarda cada línea para la evidencia.

En Windows la consola puede ser cp1252 y no imprimir «→» o «·»; para eso la
impresión usa una versión *segura* del texto, mientras la bitácora (que se
guarda como UTF-8 en la evidencia) conserva el original.
"""

from __future__ import annotations

import re
import sys

_REEMPLAZOS = {
    "→": "->", "·": "-", "✓": "OK", "⚠": "!!", "⚖": "==", "🗳": "[voto]",
    "«": '"', "»": '"',
}

# En modo breve solo pasan a la consola los encabezados de fase, los
# veredictos y los cierres; el registro (y por tanto el archivo de evidencia)
# conserva TODAS las líneas.
_PATRON_BREVE = re.compile(
    r"\[Fase|Resoluci[óo]n del conflicto|APROBADO|RECHAZADO|^[=]{{10,}}|"
    r"Informe escrito|Evidencia escrita|proyecto=|Equipo LLM|Tope de rondas|"
    r"Brief|Borrador"
)


def _seguro(msg: str) -> str:
    try:
        encoding = sys.stdout.encoding or "utf-8"
        msg.encode(encoding)
        return msg
    except (UnicodeEncodeError, LookupError):
        for simbolo, reemplazo in _REEMPLAZOS.items():
            msg = msg.replace(simbolo, reemplazo)
        try:
            msg.encode(sys.stdout.encoding or "utf-8")
        except (UnicodeEncodeError, LookupError):
            msg = msg.encode("ascii", "replace").decode("ascii")
        return msg


class Bitacora:
    def __init__(self) -> None:
        self.lineas: list[str] = []
        self.breve = False  # con True, la consola muestra solo lo esencial

    def log(self, msg: str = "") -> None:
        if not self.breve or _PATRON_BREVE.search(msg):
            print(_seguro(msg))
        self.lineas.append(msg)

    def volcado(self) -> str:
        return "\n".join(self.lineas)

    def limpiar(self) -> None:
        self.lineas = []


BITACORA = Bitacora()
