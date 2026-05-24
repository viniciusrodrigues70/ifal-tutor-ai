import os
import json

def salvar_avaliacao_json(dados, nome_arquivo):
    arquivo_existe = os.path.exists(nome_arquivo)
    conteudo = []
    
    if arquivo_existe:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            try:
                conteudo = json.load(f)
            except:
                conteudo = []
    
    conteudo.append(dados)
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, indent=4, ensure_ascii=False)