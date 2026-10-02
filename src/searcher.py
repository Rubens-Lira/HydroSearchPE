from preprocessor import tokenizar_e_limpar
from indexer import Indexador

class Buscador:
    def __init__(self, indexador: Indexador):
        self.indexador = indexador

    def buscar(self, consulta: str) -> list:
        """
        Recebe uma string de consulta, tokeniza e busca os documentos 
        que contêm todos os termos (interseção booleana AND).
        Retorna uma lista de tuplas: (doc_id, texto_do_documento).
        """
        tokens_consulta = tokenizar_e_limpar(consulta)
        
        if not tokens_consulta:
            return []

        # Pega as listas de documentos para cada termo da consulta
        conjuntos_docs = []
        for termo in tokens_consulta:
            if termo in self.indexador.indice_invertido:
                # Documentos que contêm o termo
                docs_termo = set(self.indexador.indice_invertido[termo].keys())
                conjuntos_docs.append(docs_termo)
            else:
                # Se pelo menos um termo não existe no índice, o AND retorna vazio
                return []

        # Faz a interseção dos documentos (todos os termos devem aparecer)
        docs_resultado_ids = set.intersection(*conjuntos_docs)

        # Retorna os documentos encontrados com seus respectivos textos
        resultados = []
        for doc_id in docs_resultado_ids:
            texto = self.indexador.documentos.get(doc_id, "")
            resultados.append((doc_id, texto))

        return resultados

# --- Bloco de Teste ---
if __name__ == "__main__":
    from crawler import APACrawler

    # 1. Instancia componentes
    crawler = APACrawler()
    idx = Indexador()

    # 2. Indexa os boletins simulados
    boletins = crawler.simular_coleta_boletins()
    for b in boletins:
        idx.adicionar_documento(b["doc_id"], b["texto"])

    # 3. Inicializa o buscador
    buscador = Buscador(idx)

    # 4. Testa consultas
    consulta_teste = "chuvas fortes"
    print(f"--- Resultado da busca por: '{consulta_teste}' ---")
    resultados = buscador.buscar(consulta_teste)

    for doc_id, texto in resultados:
        print(f"Doc ID {doc_id}: {texto}\n")