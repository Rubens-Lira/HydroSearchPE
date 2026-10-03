# 💧 HydroSearchPE

O **HydroSearchPE** é um projeto de Recuperação de Informação desenvolvido para facilitar a busca por informações nos conteúdos disponibilizados pela **Agência Pernambucana de Águas e Clima (APAC)**.

Futuramente, o sistema terá como objetivo abranger os diferentes conteúdos e documentos disponíveis no site da APAC.

## 🚧 Protótipo

Atualmente, o projeto encontra-se em fase de protótipo, utilizando os **boletins da APAC** como primeiro conjunto de documentos para desenvolvimento e testes do sistema.

Novas funcionalidades e fontes de informação serão adicionadas conforme o desenvolvimento do projeto.

## ⚙️ Como executar

### 1. Clone o repositório

```bash
git clone URL_DO_REPOSITORIO
cd HydroSearchPE
```

### 2. Crie o ambiente virtual

```bash
python3 -m venv venv
```

### 3. Ative o ambiente virtual

```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Baixe os boletins da APAC

```bash
python src/crawler.py
```

### 6. Execute o sistema

```bash
streamlit run src/app.py
```

Depois, acesse no navegador:

```text
http://localhost:8501
```

## 👥 Grupo

- Keila Isabelle
- Rubens Lira
- Victor Gustavo
  

## 📚 Projeto acadêmico

**Instituição:** [Institito Federal de Pernambuco]  
**Curso:** [Tecnologia em Sistemas para Internet]  
**Disciplina:** [Recuperação da Informação]  
**Professor:** [Allan Lima]

---

*Projeto em desenvolvimento.*
