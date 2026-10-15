#!/usr/bin/env python3
"""Valida una CURP mediante expresiones regulares.

Uso:
    python validar_curp.py                 # pide la entrada por teclado
    python validar_curp.py HEGG560427MVZRRL04   # recibe la CURP como argumento

Imprime "true" si la cadena cumple el formato de CURP, "false" en caso contrario.
"""
import re
import sys

# Estructura de la CURP (18 caracteres):
#  1      letra inicial del primer apellido
#  2      primera vocal interna del primer apellido (o X)
#  3-4    iniciales del segundo apellido y del nombre
#  5-10   fecha de nacimiento AAMMDD
#  11     sexo: H (hombre), M (mujer) o X (no binario)
#  12-13  clave de entidad federativa (o NE = nacido en el extranjero)
#  14-16  primeras consonantes internas de apellido paterno, materno y nombre
#  17     homoclave (dígito o letra)
#  18     dígito verificador
PATRON_CURP = re.compile(
    r"[A-Z]"                                   # 1
    r"[AEIOUX]"                                # 2
    r"[A-Z]{2}"                                # 3-4
    r"\d{2}"                                   # AA
    r"(?:0[1-9]|1[0-2])"                       # MM
    r"(?:0[1-9]|[12]\d|3[01])"                 # DD
    r"[HMX]"                                   # sexo
    r"(?:AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)"  # entidad
    r"[B-DF-HJ-NP-TV-Z]{3}"                    # consonantes internas
    r"[A-Z\d]"                                 # homoclave
    r"\d"                                      # dígito verificador
)


def es_curp_valida(cadena: str) -> bool:
    return PATRON_CURP.fullmatch(cadena) is not None


def main() -> None:
    entrada = sys.argv[1] if len(sys.argv) > 1 else input("CURP: ")
    print(str(es_curp_valida(entrada.strip())).lower())


if __name__ == "__main__":
    main()
