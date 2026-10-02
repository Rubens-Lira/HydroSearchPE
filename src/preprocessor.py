import re
import unicodedata
import nltk
from nltk.corpus import stopwords

# Garante que as stop words do NLTK estão disponíveis no ambiente
try:
    STOP_WORDS = set(stopwords.words('portuguese'))
except LookupError:
    nltk.download('stopwords')
    STOP_WORDS = set(stopwords.words('portuguese'))

def normalizar_texto(texto: str) -> str:
    """
    Realiza o case-folding (conversão para minúsculas) e 
    a remoção de acentos/diacríticos (normalização).
    """
    if not isinstance(texto, str):
        return ""
    
    # 1. Case-folding (letras minúsculas)
    texto = texto.lower()
    
    # 2. Remover acentos (normalização NFD para separar o caractere do acento)
    texto_nfd = unicodedata.normalize('NFD', texto)
    texto_sem_acento = ''.join(c for c in texto_nfd if unicodedata.category(c) != 'Mn')
    
    return texto_sem_acento

def tokenizar_e_limpar(texto: str) -> list:
    """
    Transforma o texto bruto em uma lista de tokens limpos:
    - Normaliza (sem acentos, minúsculas)
    - Tokeniza (separa palavras)
    - Remove stop words e termos irrelevantes
    """
    # Normaliza o texto bruto
    texto_normalizado = normalizar_texto(texto)
    
    # Tokenização: extrai apenas sequências de letras/palavras usando expressão regular
    tokens = re.findall(r'\b[a-zA-Záéíóúâêîôûãõç]+\b', texto_normalizado)
    
    # Filtragem: remove stop words e palavras de apenas 1 letra
    tokens_filtrados = [
        token for token in tokens 
        if token not in STOP_WORDS and len(token) > 1
    ]
    
    return tokens_filtrados

# --- Bloco de Teste Rápido ---
if __name__ == "__main__":
    exemplo_texto = "A APAC emite alerta máximo de chuvas fortes para a Região Metropolitana do Recife nesta terça-feira!"
    
    print("Texto original:", exemplo_texto)
    print("Tokens processados:", tokenizar_e_limpar(exemplo_texto))