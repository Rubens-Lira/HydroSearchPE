import re

import streamlit as st

from extractor import extrair_boletins
from indexer import Indexador
from searcher import Buscador


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="HydroSearchPE",
    page_icon="💧",
    layout="centered"
)


# =========================================================
# INICIALIZAÇÃO DO SISTEMA
# =========================================================

@st.cache_resource
def inicializar_sistema():

    indexador = Indexador()

    boletins = extrair_boletins()

    for doc_id, boletim in enumerate(
        boletins,
        start=1
    ):

        indexador.adicionar_documento(
            doc_id=doc_id,
            texto=boletim["texto"],
            titulo=boletim["titulo"],
            arquivo=boletim["arquivo"]
        )

        boletim["doc_id"] = doc_id

    buscador = Buscador(indexador)

    return indexador, buscador, boletins


indexador, buscador, boletins = inicializar_sistema()


# =========================================================
# FUNÇÃO PARA ENCONTRAR UM TRECHO RELEVANTE
# =========================================================

def obter_trecho(texto, termo, tamanho=280):

    if not texto:
        return ""

    texto = " ".join(
        texto.split()
    )

    # Procura o termo no texto original,
    # ignorando maiúsculas/minúsculas.
    correspondencia = re.search(
        re.escape(termo),
        texto,
        re.IGNORECASE
    )

    # Se não encontrar, mostra apenas
    # o começo do documento.
    if not correspondencia:

        if len(texto) > tamanho:
            return texto[:tamanho] + "..."

        return texto

    inicio = max(
        0,
        correspondencia.start() - 120
    )

    fim = min(
        len(texto),
        correspondencia.end() + 160
    )

    trecho = texto[inicio:fim]

    if inicio > 0:
        trecho = "... " + trecho

    if fim < len(texto):
        trecho += " ..."

    return trecho


# =========================================================
# CABEÇALHO
# =========================================================

st.title("💧 HydroSearchPE")

st.caption(
    "Motor de Recuperação de Informação "
    "para boletins da APAC"
)

st.write("")


# =========================================================
# ESTATÍSTICAS
# =========================================================

total_docs, total_termos = (
    indexador.obter_estatisticas()
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "📄 Documentos",
        total_docs
    )

with col2:
    st.metric(
        "🔤 Termos indexados",
        total_termos
    )


st.write("")


# =========================================================
# CAMPO DE BUSCA
# =========================================================

consulta = st.text_input(
    "Pesquisar nos boletins",
    placeholder="Digite uma palavra, por exemplo: chuva",
    label_visibility="visible"
)


# =========================================================
# RESULTADOS
# =========================================================

if consulta.strip():

    resultados = buscador.buscar(
        consulta
    )

    # ---------------------------------------------
    # Nenhum resultado
    # ---------------------------------------------

    if not resultados:

        st.warning(
            f'Nenhum documento encontrado para "{consulta}".'
        )

    else:

        termo = resultados[0]["termo"]

        st.write("")

        st.subheader(
            f'Resultados para "{termo}"'
        )

        st.caption(
            f"{len(resultados)} documento(s) encontrado(s) "
            "ordenado(s) por relevância."
        )

        st.write("")

        # -----------------------------------------
        # Lista de resultados
        # -----------------------------------------

        for posicao, resultado in enumerate(
            resultados,
            start=1
        ):

            doc_id = resultado["doc_id"]

            texto = resultado["texto"]

            score = resultado["score"]

            metadados = (
                indexador.obter_metadados(
                    doc_id
                )
            )

            titulo = metadados.get(
                "titulo",
                "Documento sem título"
            )

            arquivo = metadados.get(
                "arquivo",
                ""
            )

            # -------------------------------------
            # Card
            # -------------------------------------

            with st.container(
                border=True
            ):

                # Título
                st.markdown(
                    f"### {posicao}. {titulo}"
                )

                # Nome do arquivo
                st.caption(
                    f"📁 {arquivo}"
                )

                # Score
                st.write(
                    f"**Relevância:** "
                    f"{score:.6f}"
                )

                # Trecho
                trecho = obter_trecho(
                    texto,
                    termo
                )

                st.write(
                    trecho
                )

                # ---------------------------------
                # Botão do PDF
                # ---------------------------------

                caminho_pdf = None

                for boletim in boletins:

                    if boletim["doc_id"] == doc_id:

                        caminho_pdf = boletim.get(
                            "caminho"
                        )

                        break

                if caminho_pdf:

                    try:

                        with open(
                            caminho_pdf,
                            "rb"
                        ) as arquivo_pdf:

                            dados_pdf = (
                                arquivo_pdf.read()
                            )

                        st.download_button(
                            label="📄 Abrir / baixar PDF",
                            data=dados_pdf,
                            file_name=arquivo,
                            mime="application/pdf",
                            key=f"pdf_{doc_id}"
                        )

                    except Exception:
                        st.caption(
                            "PDF não disponível para visualização."
                        )

            st.write("")


# =========================================================
# DOCUMENTOS INDEXADOS
# =========================================================

with st.expander(
    "📚 Documentos indexados"
):

    for boletim in boletins:

        st.write(
            f"📄 **{boletim['titulo']}**"
        )

        st.caption(
            boletim["arquivo"]
        )


# =========================================================
# SOBRE O SISTEMA
# =========================================================

with st.expander(
    "ℹ️ Sobre o sistema"
):

    st.markdown(
        """
        O **HydroSearchPE** é um protótipo de
        Recuperação de Informação desenvolvido
        utilizando documentos públicos da APAC.

        **Etapas do sistema:**

        1. Coleta dos boletins;
        2. Extração do texto dos PDFs;
        3. Pré-processamento;
        4. Tokenização;
        5. Remoção de stop words;
        6. Construção do índice invertido;
        7. Cálculo de TF-IDF;
        8. Ranking dos documentos por relevância.

        Atualmente, a busca utiliza uma palavra por vez.
        """
    )