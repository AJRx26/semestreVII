import re, glob, csv
from collections import Counter
from pypdf import PdfReader
import nltk
from nltk.corpus import stopwords

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

freq_total = Counter()   # veces que aparece cada palabra en total
freq_docs = Counter()    # en cuántos artículos aparece
bigramas = Counter()     # pares de palabras consecutivas

pdfs = glob.glob("ArticulosPrimarios/ACM/*.pdf", recursive=True)
print(f"Procesando {len(pdfs)} PDF...")

for ruta in pdfs:
    texto = quitar_referencias(extraer_texto(ruta))
    tokens = tokenizar(texto)
    if not tokens:
        print(f"⚠ Sin texto extraíble (¿escaneado?): {ruta}")
        continue
    freq_total.update(tokens)
    freq_docs.update(set(tokens))          # set() = cuenta 1 por documento
    bigramas.update(zip(tokens, tokens[1:]))

# Mostrar resultados
print("\nTOP 30 palabras (frecuencia total | nº de artículos)")
for palabra, n in freq_total.most_common(30):
    print(f"{palabra:<20} {n:>5} | {freq_docs[palabra]}/{len(pdfs)}")

print("\nTOP 20 bigramas")
for (a, b), n in bigramas.most_common(20):
    print(f"{a} {b:<20} {n}")

# Exportar a CSV para abrir en Excel
with open("frecuencias.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["palabra", "frecuencia_total", "articulos"])
    for palabra, n in freq_total.most_common(200):
        w.writerow([palabra, n, freq_docs[palabra]])
