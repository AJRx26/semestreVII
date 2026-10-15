#!/usr/bin/env python3

"""
- python validar_correo -> pide la entrada por teclado
- python validar_correo.py usuario@dominio.com -> recibe el correo como argumento
"""

import re
import sys

#se define el formato del correo, cada cadena 'r"..."' se concatena en una sola
PATRON_CORREO = re.compile(
    r"[A-Za-z0-9_%+\-]+(?:\.[A-Za-z0-9_%+\-]+)*" # parte previa al @ (abraham.nunez)
    r"@" # la parte del @ (a)
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?\.)+" # parte del dominio (gmail.)
    r"[A-Za-z]{2,}" # extension (com)
)

#Funcion que hace la validacion del correo
def es_correo_valido(cadena: str) -> bool:
    return PATRON_CORREO.fullmatch(cadena) is not None

#Funcion que retorna la validacion
def main() -> None:
    entrada = sys.argv[1] if len(sys.argv) > 1 else input("Correo: ")
    print(str(es_correo_valido(entrada.strip())).lower())

if __name__ == "__main__":
    main()
