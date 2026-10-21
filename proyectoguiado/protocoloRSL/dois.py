
import csv
import json
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def consultar(url):
    """Consulta una API y devuelve sus datos JSON."""
    request = Request(
        url,
        headers={"User-Agent": "DOI-Checker/1.0"}
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def verificar(doi):
    resultado = {
        "doi": doi,
        "estado": "",
        "tipo": "",
        "titulo": "",
        "autores": "",
        "fecha": "",
        "editorial": "",
        "url": ""
    }

    # Detecta identificadores incompletos o mal formados.
    if not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
        resultado["estado"] = "DOI incompleto o mal formado"
        return resultado

    doi_url = quote(doi, safe="")
    errores = []

    # Primero consulta Crossref.
    try:
        data = consultar(
            f"https://api.crossref.org/works/{doi_url}"
        )["message"]

        resultado["estado"] = "Registrado en Crossref"
        resultado["titulo"] = " ".join(data.get("title", []))
        resultado["tipo"] = data.get("type", "")
        resultado["editorial"] = data.get("publisher", "")
        resultado["url"] = data.get("URL", "")

        autores = data.get("author", [])
        resultado["autores"] = "; ".join(
            " ".join(filter(None, [
                a.get("given"), a.get("family")
            ]))
            for a in autores
        )

        fechas = (
            data.get("published-print")
            or data.get("published-online")
            or data.get("published")
            or data.get("created")
            or {}
        )
        partes = fechas.get("date-parts", [[]])[0]
        resultado["fecha"] = "-".join(map(str, partes))

        return resultado

    except HTTPError as e:
        errores.append(f"Crossref HTTP {e.code}")
    except (URLError, TimeoutError, json.JSONDecodeError) as e:
        errores.append(f"Crossref: {type(e).__name__}")

    time.sleep(0.15)

    # Si no aparece en Crossref, prueba DataCite.
    try:
        data = consultar(
            f"https://api.datacite.org/dois/{doi_url}"
        )["data"]["attributes"]

        resultado["estado"] = "Registrado en DataCite"
        resultado["titulo"] = "; ".join(
            t.get("title", "")
            for t in data.get("titles", [])
        )
        resultado["tipo"] = (
            data.get("types", {}).get("resourceTypeGeneral", "")
        )
        resultado["autores"] = "; ".join(
            c.get("name", "")
            for c in data.get("creators", [])
        )
        resultado["fecha"] = str(
            data.get("publicationYear") or ""
        )
        resultado["editorial"] = data.get("publisher", "")
        resultado["url"] = data.get("url", "")

        return resultado

    except HTTPError as e:
        if e.code != 404:
            errores.append(f"DataCite HTTP {e.code}")
    except (URLError, TimeoutError, json.JSONDecodeError, KeyError) as e:
        errores.append(f"DataCite: {type(e).__name__}")

    resultado["estado"] = (
        "Error de consulta: " + "; ".join(errores)
        if any("HTTP" not in e for e in errores)
        else "No encontrado en Crossref/DataCite; revisar"
    )
    return resultado


def main():
    if len(sys.argv) != 3:
        print(
            "Uso: python verificar_doi.py doi.txt resultados.csv"
        )
        sys.exit(1)

    entrada, salida = sys.argv[1:3]

    with open(entrada, encoding="utf-8-sig") as archivo:
        dois = []
        for linea in archivo:
            # Permite pegar DOI de una tabla Markdown.
            linea = linea.strip().strip("|").strip()
            if not linea or linea.startswith("<br>"):
                continue
            if re.fullmatch(r"[-:\s]+", linea):
                continue
            dois.append(linea)

    # Elimina duplicados sin alterar el orden.
    dois = list(dict.fromkeys(dois))
    resultados = []

    for i, doi in enumerate(dois, start=1):
        print(f"[{i}/{len(dois)}] {doi}")
        try:
            resultados.append(verificar(doi))
        except Exception as e:
            resultados.append({
                "doi": doi,
                "estado": f"Error inesperado: {type(e).__name__}"
            })
        time.sleep(0.15)

    columnas = [
        "doi", "estado", "tipo", "titulo",
        "autores", "fecha", "editorial", "url"
    ]

    with open(salida, "w", newline="", encoding="utf-8-sig") as archivo:
        writer = csv.DictWriter(
            archivo, fieldnames=columnas, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nTerminado. Resultados guardados en: {salida}")


if __name__ == "__main__":
    main()

