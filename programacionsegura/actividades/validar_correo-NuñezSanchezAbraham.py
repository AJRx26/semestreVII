#!/usr/bin/env python3
"""Valida un correo electrónico mediante expresiones regulares.

Uso:
    python validar_correo.py                      # pide la entrada por teclado
    python validar_correo.py usuario@dominio.com  # recibe el correo como argumento

Imprime "true" si la cadena cumple el formato de correo, "false" en caso contrario.
"""
import re
import sys

# Parte local: letras, dígitos y _ % + - ; los puntos solo pueden ir entre
# segmentos (sin punto al inicio, al final ni dos seguidos).
# Dominio: etiquetas de letras/dígitos/guiones (sin guion al inicio o final)
# separadas por puntos, terminando en un TLD de al menos 2 letras.
PATRON_CORREO = re.compile(
    r"[A-Za-z0-9_%+\-]+(?:\.[A-Za-z0-9_%+\-]+)*"
    r"@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,}"
)


def es_correo_valido(cadena: str) -> bool:
    return PATRON_CORREO.fullmatch(cadena) is not None


def main() -> None:
    entrada = sys.argv[1] if len(sys.argv) > 1 else input("Correo: ")
    print(str(es_correo_valido(entrada.strip())).lower())


if __name__ == "__main__":
    main()
