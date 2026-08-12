import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# 1. Localiza a pasta onde este arquivo está
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# 2. Pega as variáveis e limpa espaços extras (.strip)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
MONGO_URI = os.getenv("MONGO_URI", "").strip()

# --- BLOCO DE DIAGNÓSTICO ---
if not MONGO_URI:
    print(f"\n❌ ERRO: O arquivo .env foi achado, mas a variável MONGO_URI está vazia!")
    exit(1)

mascarado = MONGO_URI[:15] + "..." + MONGO_URI[-10:]
print(f"✅ Arquivo .env carregado com sucesso!")
print(f"🔗 Link detectado: {mascarado}")
# -----------------------------

try:
    # 3. Conexão com o Banco de Dados
    client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    db = client["tutorbot"]

    # Coleções
    colecao_hist = db["historicos"]
    colecao_banco = db["banco_questoes"]
    colecao_avaliacoes = db["avaliacoes"]
    ARQUIVO_AVALIACOES = BASE_DIR / "avaliacoes.json"
    
    # Teste de conexão real
    client.admin.command('ping')
    print("Conexão com MongoDB estabelecida!")

except Exception as e:
    print(f"\n❌ ERRO AO CONECTAR NO MONGO:")
    print(f"Mensagem: {e}")
    exit(1)