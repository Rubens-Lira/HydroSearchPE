import os
import requests
from bs4 import BeautifulSoup
import pdfplumber

class APACrawler:
    def __init__(self, pasta_dados="data/raw_pdfs"):
        self.pasta_dados = pasta_dados
        # Cria a pasta de dados se não existir
        os.makedirs(self.pasta_dados, exist_ok=True)
        
        # URL base de exemplo da APAC (página de avisos meteorológicos / boletins)
        self.url_base = "http://www.apac.pe.gov.br/"

    def extrair_texto_pdf(self, caminho_pdf: str) -> str:
        """Extrai o texto completo de um arquivo PDF usando pdfplumber."""
        texto_completo = ""
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
        except Exception as e:
            print(f"Erro ao ler o PDF {caminho_pdf}: {e}")
        return texto_completo

    def simular_coleta_boletins(self):
        """
        Retorna uma lista de boletins simulados com dados reais do contexto da APAC,
        para você conseguir testar o indexador imediatamente mesmo sem conexão ativa.
        """
        boletins_exemplo = [
            {
                "doc_id": 101,
                "titulo": "Aviso Meteorológico - Chuvas Moderadas a Fortes",
                "texto": "A APAC emite aviso meteorológico indicando chuvas moderadas a fortes para a Região Metropolitana do Recife e Zona da Mata norte nas próximas 24 horas."
            },
            {
                "doc_id": 102,
                "titulo": "Boletim Hidrológico - Nível de Rios",
                "texto": "O monitoramento hidrológico indica elevação no nível do Rio Capibaribe devido às precipitações acumuladas na bacia hidrográfica."
            },
            {
                "doc_id": 103,
                "titulo": "Alerta de Temperaturas Elevadas",
                "texto": "Sertão de Pernambuco registra índices de umidade relativa do ar abaixo dos níveis críticos, com temperaturas máximas atingindo 38 graus Celsius."
            }
        ]
        return boletins_exemplo

    def coletar_do_site(self):
        """
        Faz uma requisição HTTP básica para buscar links de boletins ou avisos no site da APAC.
        """
        print(f"Acessando o portal da APAC em: {self.url_base} ...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(self.url_base, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Exemplo: Procurar por links de notícias ou boletins
                links = []
                for a in soup.find_all('a', href=True):
                    if 'boletim' in a['href'].lower() or 'aviso' in a['href'].lower():
                        links.append(a['href'])
                print(f"Conexão bem-sucedida! Encontrados {len(links)} links potenciais.")
                return links
            else:
                print(f"Falha na requisição. Status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Erro de conexão com o site da APAC (provável bloqueio ou instabilidade): {e}")
            print("Dica: Utilize dados locais ou simulações para alimentar seu motor de busca.")
            return []

# --- Bloco de Teste ---
if __name__ == "__main__":
    crawler = APACrawler()
    
    print("--- Testando a simulação de boletins da APAC ---")
    boletins = crawler.simular_coleta_boletins()
    for b in boletins:
        print(f"[{b['doc_id']}] {b['titulo']}")
        print(f"Trecho: {b['texto'][:60]}...\n")