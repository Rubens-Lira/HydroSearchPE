import streamlit as st
from crawler import APACrawler
from indexer import Indexador
from searcher import Buscador

# Configuração da página do Streamlit
st.set_page_config(
    page_title="APAC Search - Motor de Busca",
    page_icon="💧",
    layout="wide"
)

# Carregamento e indexação inicial (usando cache para otimizar)
@st.cache_resource
def inicializar_sistema():
    crawler = APACrawler()
    indexador = Indexador()
    
    # Carrega e indexa os boletins simulados (ou futuros PDFs)
    boletins = crawler.simular_coleta_boletins()
    for b in boletins:
        indexador.adicionar_documento(b["doc_id"], b["texto"])
        
    buscador = Buscador(indexador)
    return indexador, buscador, boletins

indexador, buscador, boletins = inicializar_sistema()

# --- Layout da Aplicação ---
st.title("💧 APAC Search Engine")
st.markdown("Motor de Recuperação de Informação para dados hidrometeorológicos da **APAC** (Agência Pernambucana de Águas e Clima).")

# Barra lateral com estatísticas do sistema (Conceitos da disciplina)
st.sidebar.header("📊 Estatísticas do Índice")
total_docs, total_termos = indexador.obter_estatisticas()
st.sidebar.metric("Documentos Indexados", total_docs)
st.sidebar.metric("Termos no Vocabulário", total_termos)

st.sidebar.markdown("---")
st.sidebar.markdown("**Funcionalidades implementadas:**")
st.sidebar.text("✓ Tokenização & Case-Folding")
st.sidebar.text("✓ Remoção de Stop Words")
st.sidebar.text("✓ Normalização (Sem acentos)")
st.sidebar.text("✓ Índice Invertido Posicional")

# Caixa de Pesquisa Principal
consulta = st.text_input("Digite sua consulta (ex: *chuvas fortes*, *rio capibaribe*, *sertão*):", "")

if consulta:
    st.markdown(f"### Resultados para: *{consulta}*")
    resultados = buscador.buscar(consulta)
    
    if resultados:
        st.success(f"Foram encontrados {len(resultados)} documento(s) relevante(s).")
        for doc_id, texto in resultados:
            with st.container():
                st.info(f"**Documento ID:** {doc_id}")
                st.write(f"**Conteúdo:** {texto}")
                st.markdown("---")
    else:
            st.warning("Nenhum documento encontrado para esta consulta.")

# Seção para visualizar os documentos brutos carregados
with st.expander("📂 Ver Boletins / Documentos Base da Base de Dados"):
    for b in boletins:
        st.markdown(f"**[{b['doc_id']}] {b['titulo']}**")
        st.text(b['texto'])
        st.markdown("---")