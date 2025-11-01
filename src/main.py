import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from datetime import datetime

# Carrega variáveis do .env
load_dotenv()

# Função para extrair texto limpo de uma URL
def extract_text_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts e estilos
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        texto = soup.get_text(separator=' ')

        # Limpa espaços extras
        linhas = (line.strip() for line in texto.splitlines())
        partes = (frase.strip() for line in linhas for frase in line.split(" "))
        texto_limpo = '\n'.join(parte for parte in partes if parte)
        return texto_limpo
    else:
        raise Exception(f"Erro ao acessar a URL. Código: {response.status_code}")

# Instancia o cliente Azure OpenAI
client = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    max_retries=0
)

# Função para traduzir texto para o idioma desejado
def translate_article(text, lang):
    messages = [
        ("system", "Você é um tradutor e formatador de artigos. Traduza o texto a seguir para o idioma solicitado e devolva o resultado em Markdown bem estruturado, com títulos, subtítulos e parágrafos."),
        ("user", f"Traduza o seguinte artigo para {lang} e formate como Markdown:\n\n{text}")
    ]
    response = client.invoke(messages)
    return response.content

# Função para salvar o resultado em um arquivo
def salvar_em_arquivo(texto, pasta="resultados", nome_base="traducao"):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = os.path.join(pasta, f"{nome_base}_{timestamp}.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto.strip())
    print(f"\n✅ Tradução salva em: {caminho}")
    
# Execução principal
if __name__ == "__main__":
    url = input("🔗 Digite a URL do artigo que deseja traduzir: ").strip()
    try:
        texto_extraido = extract_text_from_url(url)
        traducao = translate_article(texto_extraido, "pt-br")
        salvar_em_arquivo(traducao)
    except Exception as e:
        print(f"❌ Erro: {e}")