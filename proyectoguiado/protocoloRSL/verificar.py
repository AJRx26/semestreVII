
import argparse
import csv
import re
import unicodedata
from pathlib import Path


def normalizar_doi(valor):
    if not valor:
        return ""

    doi = unicodedata.normalize("NFKC", valor).strip().lower()
    doi = re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        doi
    )
    doi = re.sub(r"^doi:\s*", "", doi)

    return doi.strip().rstrip(".,;")


def leer_dois_muestra(ruta):
    with ruta.open("r", encoding="utf-8-sig") as archivo:
        return {
            normalizar_doi(linea)
            for linea in archivo
            if normalizar_doi(linea)
            and not linea.strip().startswith("#")
        }


def detectar_dialecto(archivo):
    muestra = archivo.read(8192)
    archivo.seek(0)

    try:
        return csv.Sniffer().sniff(muestra, delimiters=",;\t")
    except csv.Error:
        return csv.excel


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Comprueba cuáles DOI de una muestra aparecen "
            "en un archivo CSV de resultados."
        )
    )
    parser.add_argument(
        "csv_resultados",
        type=Path,
        help="Ruta del CSV exportado de la base de datos"
    )
    parser.add_argument(
        "txt_muestra",
        type=Path,
        help="Ruta del TXT con un DOI por línea"
    )
    parser.add_argument(
        "-c", "--columna",
        help="Nombre de la columna DOI en el CSV"
    )
    parser.add_argument(
        "-o", "--salida",
        type=Path,
        help="Ruta del reporte CSV de salida"
    )

    args = parser.parse_args()

    for ruta in (args.csv_resultados, args.txt_muestra):
        if not ruta.is_file():
            parser.error(f"No existe el archivo: {ruta}")

    dois_muestra = leer_dois_muestra(args.txt_muestra)

    if not dois_muestra:
        parser.error("El archivo TXT no contiene DOI válidos.")

    with args.csv_resultados.open(
        "r", encoding="utf-8-sig", newline=""
    ) as archivo:
        dialecto = detectar_dialecto(archivo)
        lector = csv.DictReader(archivo, dialect=dialecto)

        if not lector.fieldnames:
            parser.error("El CSV no contiene encabezados.")

        if args.columna:
            columna = args.columna
        else:
            posibles = [
                nombre for nombre in lector.fieldnames
                if nombre.strip().lower() == "doi"
            ]

            if len(posibles) == 1:
                columna = posibles[0]
            else:
                print("Columnas disponibles:")
                for nombre in lector.fieldnames:
                    print(f"  - {nombre}")

                columna = input(
                    "Escribe el nombre exacto de la columna DOI: "
                ).strip()

        if columna not in lector.fieldnames:
            parser.error(f"No existe la columna: {columna}")

        encontrados = set()

        for fila in lector:
            doi = normalizar_doi(fila.get(columna, ""))
            if doi in dois_muestra:
                encontrados.add(doi)

    total = len(dois_muestra)
    porcentaje = len(encontrados) / total * 100

    salida = args.salida or args.csv_resultados.with_name(
        args.csv_resultados.stem + "_reporte_dois.csv"
    )

    with salida.open(
        "w", encoding="utf-8-sig", newline=""
    ) as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=["DOI", "Estado"]
        )
        escritor.writeheader()

        for doi in sorted(dois_muestra):
            escritor.writerow({
                "DOI": doi,
                "Estado": (
                    "Encontrado" if doi in encontrados
                    else "No encontrado"
                )
            })

    print("\n--- Resultado de la búsqueda ---")
    print(f"CSV analizado: {args.csv_resultados}")
    print(f"Muestra: {args.txt_muestra}")
    print(f"DOI de muestra: {total}")
    print(f"Encontrados: {len(encontrados)}")
    print(f"No encontrados: {total - len(encontrados)}")
    print(f"Recuperación de la muestra: {porcentaje:.1f}%")
    print(f"Reporte guardado en: {salida}")


if __name__ == "__main__":
    main()

