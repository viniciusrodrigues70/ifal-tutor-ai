from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import colecao_banco

def teclado_materias():
    materias = colecao_banco.distinct("MATERIA")
    botoes = [[InlineKeyboardButton(m, callback_data=f"mat_{m}")] for m in materias if m]
    return InlineKeyboardMarkup(botoes)

def teclado_temas(materia):
    temas = colecao_banco.distinct("CONTEUDO", {"MATERIA": materia})
    botoes = [[InlineKeyboardButton(t, callback_data=f"tema_{t}")] for t in temas if t]
    botoes.append([InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_inicio")])
    return InlineKeyboardMarkup(botoes)

def teclado_tipos(materia, tema):
    tipos = colecao_banco.distinct("TIPO", {"MATERIA": materia, "CONTEUDO": tema})
    botoes = [[InlineKeyboardButton(tipo, callback_data=f"type_{tipo}")] for tipo in tipos if tipo]
    botoes.append([InlineKeyboardButton("⬅️ Mudar Tema", callback_data=f"mat_{materia}")])
    return InlineKeyboardMarkup(botoes)

def teclado_likert():
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{i}⭐", callback_data=f"nota_{i}") for i in range(1, 6)]])

def teclado_parar():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Parar e Mudar Assunto", callback_data="voltar_inicio")]])