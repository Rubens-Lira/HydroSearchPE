from collections import defaultdict
from preprocessor import tokenizar_e_limpar

class Indexador:
    def __init__(self):
        # Estrutura do Índice Invertido:
        # { termo: { doc_id: [pos1, pos2, ...] } }
        self.indice_invertido = defaultdict(lambda: defaultdict(list))
        self.documentos = {} # Armazena o texto original ou metadados por doc_id

    def adicionar_documento(self, doc_id: int, texto: str):
        """
        Adiciona um documento ao sistema, tokeniza o texto 
        e atualiza o índice invertido posicional.
        """
        self.documentos[doc_id] = texto
        tokens = tokenizar_e_limpar(texto)
        
        # Percorre os tokens e registra suas posições exatas no documento
        posicao = 0
        for token in tokens:
            self.indice_invertido[token][doc_id].append(posicao)
            posicao += 1

    def obter_estatisticas(self):
        """Retorna estatísticas básicas do índice construído"""
        total_termos = len(self.indice_invertido)
        total_docs = len(self.documentos)
        return total_docs, total_termos

# --- Bloco de Teste ---
if __name__ == "__main__":
    idx = Indexador()

    # Simulando alguns boletins da APAC
    doc1 = "A APAC emite alerta máximo de chuvas fortes na Região Metropolitana do Recife."
    doc2 = "Alerta de chuvas fortes e risco de alagamentos na Região Metropolitana."

    idx.adicionar_documento(doc_id=1, texto=doc1)
    idx.adicionar_documento(doc_id=2, texto=doc2)

    docs_totais, termos_totais = idx.obter_estatisticas()
    print(f"Documentos indexados: {docs_totais}")
    print(f"Termos únicos no vocabulário: {termos_totais}\n")

    print("--- Amostra do Índice Invertido (Termo -> {DocID: Posições}) ---")
    for termo, postings in list(idx.indice_invertido.items())[:5]:
        print(f"Termo '{termo}': {dict(postings)}")