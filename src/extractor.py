from pathlib import Path

from pypdf import PdfReader


RAIZ_PROJETO = (
    Path(__file__).resolve().parent.parent
)

PASTAS_PDFS = [
    RAIZ_PROJETO / "data" / "pdfs",
    RAIZ_PROJETO / "src" / "data" / "pdfs",
]


def extrair_texto_pdf(caminho_pdf):

    leitor = PdfReader(
        caminho_pdf
    )

    paginas = []

    for pagina in leitor.pages:

        texto = pagina.extract_text()

        if texto:
            paginas.append(texto)

    return "\n".join(
        paginas
    )


def extrair_boletins():

    documentos = []

    arquivos_encontrados = set()

    for pasta in PASTAS_PDFS:

        if not pasta.exists():
            continue

        for pdf in pasta.glob("*.pdf"):

            caminho_real = pdf.resolve()

            if caminho_real in arquivos_encontrados:
                continue

            arquivos_encontrados.add(
                caminho_real
            )

            print(
                f"Extraindo: {pdf.name}"
            )

            texto = extrair_texto_pdf(
                pdf
            )

            documentos.append({
                "titulo": pdf.stem,
                "arquivo": pdf.name,
                "caminho": str(pdf),
                "texto": texto
            })

    return documentos


if __name__ == "__main__":

    documentos = extrair_boletins()

    print(
        f"\nDocumentos encontrados: "
        f"{len(documentos)}"
    )

    for documento in documentos:

        print("\n" + "=" * 60)

        print(
            documento["titulo"]
        )

        print("=" * 60)

        print(
            documento["texto"][:1000]
        )