import math

from preprocessor import tokenizar_e_limpar
from indexer import Indexador


class Buscador:

    def __init__(self, indexador: Indexador):
        self.indexador = indexador

    def buscar(self, consulta: str) -> list:
        """
        Realiza busca por relevância utilizando TF-IDF.

        Atualmente o protótipo foi pensado para consultas
        de uma palavra.

        Retorna uma lista de dicionários contendo:

        - doc_id
        - texto
        - score
        - termo
        """

        # ---------------------------------------------
        # 1. Pré-processamento da consulta
        # ---------------------------------------------

        tokens = tokenizar_e_limpar(
            consulta
        )

        if not tokens:
            return []

        # Para este primeiro protótipo,
        # utilizaremos apenas a primeira palavra.
        termo = tokens[0]

        # ---------------------------------------------
        # 2. Verifica se o termo existe no índice
        # ---------------------------------------------

        if termo not in self.indexador.indice_invertido:
            return []

        # ---------------------------------------------
        # 3. Quantidade total de documentos
        # ---------------------------------------------

        total_documentos = len(
            self.indexador.documentos
        )

        # ---------------------------------------------
        # 4. Documentos que possuem o termo
        # ---------------------------------------------

        documentos_termo = (
            self.indexador.obter_documentos_termo(
                termo
            )
        )

        quantidade_documentos_termo = len(
            documentos_termo
        )

        if quantidade_documentos_termo == 0:
            return []

        # ---------------------------------------------
        # 5. Calcula IDF
        # ---------------------------------------------

        idf = math.log(
            total_documentos /
            quantidade_documentos_termo
        )

        resultados = []

        # ---------------------------------------------
        # 6. Calcula TF-IDF de cada documento
        # ---------------------------------------------

        for doc_id in documentos_termo:

            frequencia = (
                self.indexador
                .obter_frequencia_termo(
                    termo,
                    doc_id
                )
            )

            tamanho_documento = (
                self.indexador
                .tamanho_documentos
                .get(
                    doc_id,
                    0
                )
            )

            if tamanho_documento == 0:
                continue

            # TF
            tf = (
                frequencia /
                tamanho_documento
            )

            # TF-IDF
            score = tf * idf

            texto = (
                self.indexador
                .obter_documento(
                    doc_id
                )
            )

            resultados.append({
                "doc_id": doc_id,
                "texto": texto,
                "score": score,
                "termo": termo,
                "tf": tf,
                "idf": idf
            })

        # ---------------------------------------------
        # 7. Ordena pela relevância
        # ---------------------------------------------

        resultados.sort(
            key=lambda resultado:
                resultado["score"],
            reverse=True
        )

        return resultados


# =========================================================
# TESTE DO BUSCADOR
# =========================================================

if __name__ == "__main__":

    idx = Indexador()

    doc1 = """
    chuva chuva chuva
    Recife apresentou chuva intensa.
    """

    doc2 = """
    O boletim apresenta informações
    sobre chuva em Pernambuco.
    """

    doc3 = """
    Informações sobre rios e reservatórios.
    """

    idx.adicionar_documento(
        1,
        doc1,
        "Boletim de Chuvas - Recife",
        "boletim1.pdf"
    )

    idx.adicionar_documento(
        2,
        doc2,
        "Boletim Climático",
        "boletim2.pdf"
    )

    idx.adicionar_documento(
        3,
        doc3,
        "Boletim de Reservatórios",
        "boletim3.pdf"
    )

    buscador = Buscador(idx)

    resultados = buscador.buscar(
        "chuva"
    )

    print("=" * 60)
    print("BUSCA: chuva")
    print("=" * 60)

    for resultado in resultados:

        print(
            f"Documento: "
            f"{resultado['doc_id']}"
        )

        print(
            f"Score TF-IDF: "
            f"{resultado['score']:.6f}"
        )

        print(
            f"TF: "
            f"{resultado['tf']:.6f}"
        )

        print(
            f"IDF: "
            f"{resultado['idf']:.6f}"
        )

        print("-" * 60)