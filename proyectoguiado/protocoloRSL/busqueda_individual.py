import argparse
import csv
import logging
import re
import sys
from collections import Counter
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from pypdf import PdfReader

# Silencia los avisos de fuentes de pypdf (no afectan el conteo)
logging.getLogger("pypdf").setLevel(logging.ERROR)

nltk.download("stopwords", quiet=True)

# Stopwords en inglés y español + ruido típico de artículos académicos
STOP = set(stopwords.words("english")) | set(stopwords.words("spanish"))
STOP |= {"also", "et", "al", "fig", "figure", "table", "using", "used",
         "based", "paper", "study", "research", "results", "however",
         "doi", "ieee", "springer", "elsevier", "journal", "vol"}


def extraer_texto(ruta):
    lector = PdfReader(ruta)
    return " ".join((p.extract_text() or "") for p in lector.pages)


def quitar_referencias(texto):
    # Corta el texto desde la última aparición de "References", etc.
    coincidencias = list(re.finditer(
        r"\b(references|referencias|bibliography|bibliografía)\b", texto, re.I))
    return texto[:coincidencias[-1].start()] if coincidencias else texto


def tokenizar(texto):
    palabras = re.findall(r"[a-záéíóúñü]{3,}", texto.lower())
    return [p for p in palabras if p not in STOP]


def main():
    parser = argparse.ArgumentParser(
        description="Cuenta las palabras y bigramas más frecuentes de un PDF.")
    parser.add_argument("pdf", help="Ruta del archivo PDF a analizar")
    parser.add_argument("-n", "--top", type=int, default=30,
                        help="Cuántas palabras mostrar (default: 30)")
    parser.add_argument("-b", "--bigramas", type=int, default=20,
                        help="Cuántos bigramas mostrar (default: 20)")
    parser.add_argument("--con-referencias", action="store_true",
                        help="No recortar la sección de referencias")
    parser.add_argument("--csv", action="store_true",
                        help="Guardar resultados en <nombre>_frecuencias.csv")
    args = parser.parse_args()

    ruta = Path(args.pdf)
    if not ruta.is_file():
        sys.exit(f"Error: no existe el archivo '{ruta}'")
    if ruta.suffix.lower() != ".pdf":
        sys.exit("Error: el archivo debe ser un PDF")

    texto = extraer_texto(ruta)
    if not args.con_referencias:
        texto = quitar_referencias(texto)

    tokens = tokenizar(texto)
    if not tokens:
        sys.exit("⚠ Sin texto extraíble (¿PDF escaneado?). "
                 "Usa OCR: ocrmypdf entrada.pdf salida.pdf")

    palabras = Counter(tokens)
    bigramas = Counter(zip(tokens, tokens[1:]))

    print(f"Archivo: {ruta.name}")
    print(f"Palabras analizadas (sin stopwords): {len(tokens)}")

    print(f"\nTOP {args.top} palabras")
    for palabra, n in palabras.most_common(args.top):
        print(f"{palabra:<22} {n:>5}")

    print(f"\nTOP {args.bigramas} bigramas")
    for (a, b), n in bigramas.most_common(args.bigramas):
        print(f"{a + ' ' + b:<30} {n:>5}")

    if args.csv:
        salida = ruta.with_name(f"{ruta.stem}_frecuencias.csv")
        with open(salida, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["tipo", "termino", "frecuencia"])
            for palabra, n in palabras.most_common(200):
                w.writerow(["palabra", palabra, n])
            for (a, b), n in bigramas.most_common(100):
                w.writerow(["bigrama", f"{a} {b}", n])
        print(f"\nCSV guardado en: {salida}")


if __name__ == "__main__":
    main()
