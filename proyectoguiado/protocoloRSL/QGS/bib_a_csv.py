
import csv
import sys
import bibtexparser


def convertir_bib_a_csv(archivo_bib, archivo_csv):
    # Leer el archivo BibTeX
    with open(archivo_bib, "r", encoding="utf-8-sig") as archivo:
        biblioteca = bibtexparser.load(archivo)

    # Campos que queremos conservar
    columnas = [
        "id",
        "tipo",
        "doi",
        "title",
        "author",
        "year",
        "journal",
        "booktitle",
        "publisher",
        "url",
    ]

    # Escribir el CSV
    with open(
        archivo_csv, "w", newline="", encoding="utf-8-sig"
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas,
            extrasaction="ignore",
        )
        escritor.writeheader()

        for referencia in biblioteca.entries:
            fila = {
                "id": referencia.get("ID", ""),
                "tipo": referencia.get("ENTRYTYPE", ""),
            }

            for campo in columnas:
                if campo not in ("id", "tipo"):
                    fila[campo] = referencia.get(campo, "")

            escritor.writerow(fila)

    print(f"Conversión terminada: {archivo_csv}")
    print(f"Referencias exportadas: {len(biblioteca.entries)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python bib_a_csv.py entrada.bib salida.csv")
        sys.exit(1)

    convertir_bib_a_csv(sys.argv[1], sys.argv[2])

