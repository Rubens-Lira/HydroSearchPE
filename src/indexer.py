from collections import defaultdict
from preprocessor import tokenizar_e_limpar


class Indexador:

    def __init__(self):
        # Índice invertido:
        # termo -> documento -> posições
        self.indice_invertido = defaultdict(
            lambda: defaultdict(list)
        )

        # Documento:
        # doc_id -> texto
        self.documentos = {}

        # Metadados:
        # doc_id -> informações do documento
        self.metadados = {}

        # Quantidade de tokens de cada documento
        # doc_id -> quantidade
        self.tamanho_documentos = {}

    def adicionar_documento(
        self,
        doc_id: int,
        texto: str,
        titulo: str = "",
        arquivo: str = ""
    ):

        self.documentos[doc_id] = texto

        self.metadados[doc_id] = {
            "titulo": titulo,
            "arquivo": arquivo
        }

        # Pré-processamento
        tokens = tokenizar_e_limpar(texto)

        # Guarda o tamanho do documento
        self.tamanho_documentos[doc_id] = len(tokens)

        # Construção do índice invertido posicional
        for posicao, token in enumerate(tokens):

            self.indice_invertido[token][doc_id].append(
                posicao
            )

    def obter_estatisticas(self):

        total_termos = len(
            self.indice_invertido
        )

        total_docs = len(
            self.documentos
        )

        return total_docs, total_termos

    def obter_documento(self, doc_id):

        return self.documentos.get(
            doc_id,
            ""
        )

    def obter_metadados(self, doc_id):

        return self.metadados.get(
            doc_id,
            {
                "titulo": "",
                "arquivo": ""
            }
        )

    def obter_frequencia_termo(
        self,
        termo,
        doc_id
    ):

        """
        Retorna quantas vezes um termo
        aparece em determinado documento.
        """

        if termo not in self.indice_invertido:
            return 0

        if doc_id not in self.indice_invertido[termo]:
            return 0

        return len(
            self.indice_invertido[termo][doc_id]
        )

    def obter_documentos_termo(self, termo):

        """
        Retorna os IDs dos documentos que
        possuem determinado termo.
        """

        if termo not in self.indice_invertido:
            return set()

        return set(
            self.indice_invertido[termo].keys()
        )

    def obter_termos_mais_frequentes(self, n: int = 10, min_len: int = 3):
        """
        Retorna os N termos mais frequentes no acervo,
        com base na contagem total no índice invertido.
        Filtra por tamanho mínimo de caracteres (padrão 3).
        """
        frequencias = []
        for termo, docs in self.indice_invertido.items():
            if len(termo) < min_len:
                continue
            total = sum(len(posicoes) for posicoes in docs.values())
            frequencias.append((termo, total))

        frequencias.sort(key=lambda item: item[1], reverse=True)
        return frequencias[:n]

    def obter_distribuicao_categorias(self):
        """
        Retorna a contagem de documentos agrupados por tipo/categoria de boletim.
        """
        categorias = {}
        for doc_id, meta in self.metadados.items():
            nome = meta.get("arquivo", "").lower()
            if "reservat" in nome:
                categoria = "Reservatórios e Barragens"
            elif "pluvio" in nome:
                categoria = "Pluviométrico (Chuvas)"
            elif "rio" in nome:
                categoria = "Monitoramento de Rios"
            elif "clim" in nome or "previsao" in nome:
                categoria = "Clima e Previsão"
            elif "acompanhamento" in nome:
                categoria = "Acompanhamento Geral"
            else:
                categoria = "Outros Boletins"

            categorias[categoria] = categorias.get(categoria, 0) + 1

        return categorias


# =========================================================
# TESTE
# =========================================================

if __name__ == "__main__":

    idx = Indexador()

    doc1 = """
    A APAC emite alerta máximo de chuvas fortes
    para a Região Metropolitana do Recife.
    """

    doc2 = """
    Alerta de chuvas fortes e risco de alagamentos
    na Região Metropolitana.
    """

    idx.adicionar_documento(
        1,
        doc1,
        "Boletim de Chuvas",
        "boletim1.pdf"
    )

    idx.adicionar_documento(
        2,
        doc2,
        "Alerta de Alagamentos",
        "boletim2.pdf"
    )

    total_docs, total_termos = (
        idx.obter_estatisticas()
    )

    print(
        f"Documentos indexados: {total_docs}"
    )

    print(
        f"Termos únicos: {total_termos}"
    )

    print(
        "Frequência de 'chuvas' no documento 1:",
        idx.obter_frequencia_termo(
            "chuvas",
            1
        )
    )