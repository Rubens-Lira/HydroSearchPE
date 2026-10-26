import re
import altair as alt
import pandas as pd
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
    "para boletins da APAC (Agência Pernambucana de Águas e Clima)"
)

st.write("")


# =========================================================
# ESTATÍSTICAS DO CORPUS
# =========================================================

total_docs, total_termos = (
    indexador.obter_estatisticas()
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "📄 Documentos Indexados",
        total_docs
    )

with col2:
    st.metric(
        "🔤 Vocabulário Único",
        f"{total_termos:,}".replace(",", ".")
    )

st.write("")


# =========================================================
# CAMPO DE BUSCA E SUGESTÕES RÁPIDAS
# =========================================================

if "input_busca" not in st.session_state:
    st.session_state["input_busca"] = ""


def definir_termo_busca(termo_sugerido):
    st.session_state["input_busca"] = termo_sugerido


consulta = st.text_input(
    "Pesquisar nos boletins",
    key="input_busca",
    placeholder="Digite uma palavra, por exemplo: chuva, alerta, rio, nivel, reservatorios...",
    label_visibility="visible"
)

# Sugestões rápidas para demonstração prática
st.caption("💡 **Sugestões para teste rápido:**")
col_sugs = st.columns(6)
sugestoes_exemplo = ["chuva", "alerta", "rio", "reservatorios", "nivel", "cemaden"]

for i, sugestao in enumerate(sugestoes_exemplo):
    with col_sugs[i]:
        st.button(
            sugestao,
            key=f"sug_{sugestao}",
            on_click=definir_termo_busca,
            args=(sugestao,),
            use_container_width=True
        )

st.write("")


# =========================================================
# RESULTADOS DA BUSCA OU PANORAMA DO ACERVO
# =========================================================

if consulta.strip():

    resultados = buscador.buscar(
        consulta
    )

    # -----------------------------------------------------
    # Nenhum resultado
    # -----------------------------------------------------
    if not resultados:

        st.warning(
            f'Nenhum documento encontrado para "{consulta}". '
            "Tente outra palavra-chave (ex: chuva, alerta, rio, nivel)."
        )

    else:

        termo = resultados[0]["termo"]

        st.subheader(
            f'Resultados para "{termo}"'
        )

        st.caption(
            f"{len(resultados)} documento(s) encontrado(s) "
            "ordenado(s) por relevância calculada via TF-IDF."
        )

        # -------------------------------------------------
        # GRÁFICO PRINCIPAL DE RI: RANKING DE RELEVÂNCIA
        # -------------------------------------------------
        with st.container(border=True):

            st.markdown("### 📊 Ranqueamento de Relevância dos Documentos (TF-IDF)")
            st.caption(
                "Este gráfico representa o **ponto central da Recuperação da Informação**: "
                "a ordenação de relevância dos documentos calculada pelo Modelo Vetorial (TF-IDF)."
            )

            # Métricas da consulta
            score_max = max(r["score"] for r in resultados)
            score_medio = sum(r["score"] for r in resultados) / len(resultados)
            idf_termo = resultados[0]["idf"]
            melhor_doc_id = resultados[0]["doc_id"]
            melhor_meta = indexador.obter_metadados(melhor_doc_id)
            melhor_titulo = melhor_meta.get("titulo", f"Doc {melhor_doc_id}")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("🏆 Top 1", f"Doc #{melhor_doc_id}", help=melhor_titulo)
            with m2:
                st.metric("📈 Score Máx.", f"{score_max:.5f}")
            with m3:
                st.metric("📊 Score Médio", f"{score_medio:.5f}")
            with m4:
                st.metric(
                    "🎯 IDF do Termo",
                    f"{idf_termo:.4f}",
                    help="Frequência Inversa do Documento: mede o poder discriminativo do termo no acervo."
                )

            st.write("")

            # Montagem do DataFrame para o gráfico
            dados_grafico = []
            for posicao, r in enumerate(resultados, start=1):
                meta = indexador.obter_metadados(r["doc_id"])
                titulo_orig = meta.get("titulo", f"Doc {r['doc_id']}")
                titulo_curto = (
                    (titulo_orig[:30] + "...")
                    if len(titulo_orig) > 30
                    else titulo_orig
                )
                rotulo = f"#{posicao} {titulo_curto}"

                dados_grafico.append({
                    "Posição": posicao,
                    "Documento": rotulo,
                    "Título Completo": titulo_orig,
                    "Score TF-IDF": r["score"],
                    "TF": r["tf"],
                    "IDF": r["idf"],
                    "Arquivo": meta.get("arquivo", "")
                })

            df_res = pd.DataFrame(dados_grafico)

            # Seletor de visualização se houver muitos documentos
            if len(df_res) > 5:
                opcoes_vis = ["Top 5", "Top 10", "Todos os Resultados"]
                if len(df_res) < 10:
                    opcoes_vis = ["Top 5", "Todos os Resultados"]

                idx_def = 1 if "Top 10" in opcoes_vis else 0

                escolha_qtd = st.radio(
                    "Exibir no gráfico:",
                    opcoes_vis,
                    index=idx_def,
                    horizontal=True
                )

                if escolha_qtd == "Top 5":
                    df_plot = df_res.head(5)
                elif escolha_qtd == "Top 10":
                    df_plot = df_res.head(10)
                else:
                    df_plot = df_res
            else:
                df_plot = df_res

            # Gráfico de Barras Horizontais com Altair
            chart_relevancia = (
                alt.Chart(df_plot)
                .mark_bar(cornerRadiusEnd=5, color="#0288D1")
                .encode(
                    x=alt.X(
                        "Score TF-IDF:Q",
                        title="Score de Relevância (TF-IDF)",
                        axis=alt.Axis(format=".4f", grid=True)
                    ),
                    y=alt.Y(
                        "Documento:N",
                        sort="-x",
                        title="Ranking e Boletim"
                    ),
                    tooltip=[
                        alt.Tooltip("Posição:Q", title="Ranking"),
                        alt.Tooltip("Título Completo:N", title="Documento"),
                        alt.Tooltip("Score TF-IDF:Q", title="Score TF-IDF", format=".6f"),
                        alt.Tooltip("TF:Q", title="TF (Term Frequency)", format=".6f"),
                        alt.Tooltip("IDF:Q", title="IDF (Inverse Doc Freq)", format=".4f"),
                        alt.Tooltip("Arquivo:N", title="Arquivo")
                    ]
                )
                .properties(
                    height=max(180, len(df_plot) * 34)
                )
                .interactive()
            )

            st.altair_chart(chart_relevancia, use_container_width=True)

            # Explicação didática dos conceitos de RI
            with st.expander("🎓 Como o Modelo de Recuperação calcula essa relevância?"):
                st.markdown(
                    r"""
                    Na disciplina de **Recuperação da Informação**, o modelo de pontuação combina dois fatores:

                    1. **TF (Term Frequency - Frequência do Termo no Documento):**
                       $$\text{TF}(t, d) = \frac{f(t, d)}{\text{total de tokens em } d}$$
                       *Normalizado pelo tamanho do documento para não favorecer textos excessivamente longos.*

                    2. **IDF (Inverse Document Frequency - Frequência Inversa do Documento):**
                       $$\text{IDF}(t) = \ln\left(\frac{N}{n_t}\right)$$
                       *Onde $N$ é o total de boletins no acervo e $n_t$ é o número de boletins contendo o termo $t$. Avalia a raridade e especificidade do termo.*

                    3. **Score Final TF-IDF:**
                       $$\text{Score}(d, q) = \text{TF}(t, d) \times \text{IDF}(t)$$
                       *Quanto maior a pontuação, mais alta a barra no gráfico e maior a prioridade do boletim no ranking.*
                    """
                )

        st.write("")

        # -------------------------------------------------
        # Lista detalhada de resultados (Cards)
        # -------------------------------------------------
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

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {posicao}. {titulo}"
                )

                st.caption(
                    f"📁 {arquivo}"
                )

                st.write(
                    f"**Relevância (TF-IDF):** "
                    f"`{score:.6f}` (TF: `{resultado['tf']:.6f}` | IDF: `{resultado['idf']:.4f}`)"
                )

                trecho = obter_trecho(
                    texto,
                    termo
                )

                st.write(
                    trecho
                )

                # Botão do PDF
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

else:

    # =====================================================
    # PANORAMA GERAL DO ACERVO (GRÁFICOS DA BASE INDEXADA)
    # =====================================================
    with st.container(border=True):

        st.markdown("### 📊 Panorama do Acervo da APAC")
        st.caption(
            "Visualização estatística dos dados processados pelo motor de RI antes de efetuar consultas. "
            "Pesquise uma palavra acima para ver o **Gráfico de Relevância TF-IDF** dos resultados!"
        )

        tab_termos, tab_categorias = st.tabs([
            "🔤 Termos Mais Frequentes",
            "📁 Categorias dos Boletins"
        ])

        with tab_termos:

            st.markdown("#### Top 10 Termos Mais Recorrentes")
            st.caption(
                "Frequência acumulada das palavras nos boletins (após tokenização e remoção de stopwords no índice invertido)."
            )

            termos_frequentes = indexador.obter_termos_mais_frequentes(n=10, min_len=3)
            df_termos = pd.DataFrame(
                termos_frequentes,
                columns=["Termo", "Ocorrências"]
            )

            chart_termos = (
                alt.Chart(df_termos)
                .mark_bar(cornerRadiusEnd=5, color="#00897B")
                .encode(
                    x=alt.X(
                        "Ocorrências:Q",
                        title="Ocorrências no Acervo",
                        axis=alt.Axis(grid=True)
                    ),
                    y=alt.Y(
                        "Termo:N",
                        sort="-x",
                        title="Termo Indexado"
                    ),
                    tooltip=[
                        alt.Tooltip("Termo:N", title="Termo"),
                        alt.Tooltip("Ocorrências:Q", title="Total de Ocorrências")
                    ]
                )
                .properties(height=320)
                .interactive()
            )

            st.altair_chart(chart_termos, use_container_width=True)

        with tab_categorias:

            st.markdown("#### Distribuição de Boletins por Categoria")
            st.caption("Classificação dos documentos catalogados da APAC no acervo.")

            dist_cat = indexador.obter_distribuicao_categorias()
            df_cat = pd.DataFrame(
                list(dist_cat.items()),
                columns=["Categoria", "Quantidade"]
            ).sort_values("Quantidade", ascending=False)

            chart_cat = (
                alt.Chart(df_cat)
                .mark_bar(cornerRadiusEnd=5, color="#3949AB")
                .encode(
                    x=alt.X(
                        "Quantidade:Q",
                        title="Quantidade de Documentos",
                        axis=alt.Axis(tickMinStep=1, grid=True)
                    ),
                    y=alt.Y(
                        "Categoria:N",
                        sort="-x",
                        title="Tipo de Boletim"
                    ),
                    tooltip=[
                        alt.Tooltip("Categoria:N", title="Categoria"),
                        alt.Tooltip("Quantidade:Q", title="Documentos")
                    ]
                )
                .properties(height=260)
                .interactive()
            )

            st.altair_chart(chart_cat, use_container_width=True)

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
        8. Ranking dos documentos por relevância e visualização em gráfico.

        Atualmente, a busca utiliza uma palavra por vez.
        """
    )