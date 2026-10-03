import re
import unicodedata
import nltk
from nltk.corpus import stopwords


try:
    STOP_WORDS = set(stopwords.words("portuguese"))
except LookupError:
    nltk.download("stopwords")
    STOP_WORDS = set(stopwords.words("portuguese"))


def normalizar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        return ""

    texto = texto.lower()

    texto_nfd = unicodedata.normalize("NFD", texto)

    texto_sem_acento = "".join(
        c for c in texto_nfd
        if unicodedata.category(c) != "Mn"
    )

    return texto_sem_acento


def tokenizar_e_limpar(texto: str) -> list:
    texto_normalizado = normalizar_texto(texto)

    tokens = re.findall(
        r"\b[a-z]+\b",
        texto_normalizado
    )

    tokens_filtrados = [
        token
        for token in tokens
        if token not in STOP_WORDS
        and len(token) > 1
    ]

    return tokens_filtrados