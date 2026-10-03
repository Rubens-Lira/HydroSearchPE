import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path


URL = "https://www.apac.pe.gov.br/mais/boletins"

# Raiz do projeto HydroSearchPE
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# Pasta onde os PDFs serão armazenados
PASTA_PDFS = RAIZ_PROJETO / "data" / "pdfs"
PASTA_PDFS.mkdir(parents=True, exist_ok=True)


def buscar_boletins():

    resposta = requests.get(URL, timeout=30)

    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")

    boletins = []

    for link in soup.find_all("a", href=True):

        titulo = link.get_text(" ", strip=True)
        href = link["href"]

        url_pdf = urljoin(URL, href)

        if ".pdf" in url_pdf.lower():

            boletins.append({
                "titulo": titulo,
                "url": url_pdf
            })

    return boletins


def baixar_pdf(boletim):

    url = boletim["url"]

    # Pega somente o nome do arquivo
    nome_arquivo = url.split("/")[-1].split("?")[0]

    caminho = PASTA_PDFS / nome_arquivo

    # Se já existir, não baixa novamente
    if caminho.exists():

        print(f"[JÁ EXISTE] {nome_arquivo}")

        return caminho

    print(f"[BAIXANDO] {nome_arquivo}")

    try:

        resposta = requests.get(
            url,
            timeout=60
        )

        resposta.raise_for_status()

        # Verifica se realmente recebemos um PDF
        content_type = resposta.headers.get("Content-Type", "")

        print(f"  Status: {resposta.status_code}")
        print(f"  Content-Type: {content_type}")
        print(f"  Tamanho: {len(resposta.content) / 1024:.1f} KB")

        caminho.write_bytes(resposta.content)

        print(f"  [SALVO] {caminho}")

        return caminho

    except requests.RequestException as erro:

        print(f"  [ERRO] Não foi possível baixar:")
        print(f"  {erro}")

        return None


if __name__ == "__main__":

    boletins = buscar_boletins()

    print(f"\nEncontrados: {len(boletins)} PDFs\n")

    for boletim in boletins:

        print("=" * 70)

        print(boletim["titulo"])
        print(boletim["url"])

        baixar_pdf(boletim)

    print("\n" + "=" * 70)

    print("COLETA FINALIZADA")

    print(f"Pasta dos PDFs: {PASTA_PDFS}")

    arquivos = list(PASTA_PDFS.glob("*.pdf"))

    print(f"PDFs salvos: {len(arquivos)}")