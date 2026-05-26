import re
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# Importando os nossos módulos recém-criados
from config import TELEGRAM_TOKEN, ARQUIVO_AVALIACOES, colecao_hist, colecao_banco, colecao_avaliacoes
from utils import salvar_avaliacao_json
import ui

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = update.effective_user.first_name
    await update.message.reply_text(
        f"Fala, {nome}! 👋 Pronto para gabaritar no Ensino Médio?\n\nEscolha uma matéria para começar o quiz:",
        reply_markup=ui.teclado_materias()
    )

async def limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    colecao_hist.delete_one({"user_id": user_id})
    await update.message.reply_text("🧹 <b>Sessão resetada.</b> Tudo limpo!", parse_mode="HTML")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    data = query.data
    await query.answer()

    if data == "voltar_inicio":
        colecao_hist.update_one({"user_id": user_id}, {"$unset": {"questao_ativa": "", "tema_atual": "", "tipo_atual": ""}})
        await query.edit_message_text("Beleza! Escolha uma matéria:", reply_markup=ui.teclado_materias())

    elif data.startswith("mat_"):
        materia = data.split("_", 1)[1]
        colecao_hist.update_one({"user_id": user_id}, {"$set": {"materia_atual": materia}}, upsert=True)
        await query.edit_message_text(f"Boa! Qual assunto de <b>{materia}</b> vamos revisar?", reply_markup=ui.teclado_temas(materia), parse_mode="HTML")

    elif data.startswith("tema_"):
        tema = data.split("_", 1)[1]
        doc_usuario = colecao_hist.find_one({"user_id": user_id}) or {}
        materia = doc_usuario.get("materia_atual")
        colecao_hist.update_one({"user_id": user_id}, {"$set": {"tema_atual": tema}}, upsert=True)
        await query.edit_message_text(f"Que estilo de questão de <b>{tema}</b> você quer?", reply_markup=ui.teclado_tipos(materia, tema), parse_mode="HTML")

    elif data.startswith("type_"):
        tipo = data.split("_", 1)[1]
        doc_usuario = colecao_hist.find_one({"user_id": user_id}) or {}
        tema = doc_usuario.get("tema_atual")
        colecao_hist.update_one({"user_id": user_id}, {"$set": {"tipo_atual": tipo}}, upsert=True)
        await enviar_questao(query, context, user_id, tema, tipo)

    elif data.startswith("nota_"):
        nota = data.split("_")[1]
        doc_usuario = colecao_hist.find_one({"user_id": user_id}) or {}
        dados = {
            "usuario_id": user_id,
            "pergunta": doc_usuario.get("ultima_entrada_usuario", "N/A"),
            "resposta_bot": doc_usuario.get("ultimo_feedback_completo", "N/A"),
            "nota_feedback": nota,
            "data_avaliacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        salvar_avaliacao_json(dados, ARQUIVO_AVALIACOES)
        colecao_avaliacoes.insert_one(dados.copy())
        await query.edit_message_text(f"✅ Feedback de {nota} ⭐ registrado! Continue focado nos estudos.")

async def enviar_questao(update_or_query, context, user_id, tema, tipo):
    doc_hist = colecao_hist.find_one({"user_id": user_id}) or {}
    questoes_vistas = doc_hist.get("questoes_vistas", [])

    pipeline = [
        {"$match": {"CONTEUDO": tema, "TIPO": tipo, "_id": {"$nin": questoes_vistas}}},
        {"$sample": {"size": 1}}
    ]
    q_list = list(colecao_banco.aggregate(pipeline))

    if not q_list:
        colecao_hist.update_one({"user_id": user_id}, {"$set": {"questoes_vistas": []}})
        q_list = list(colecao_banco.aggregate([{"$match": {"CONTEUDO": tema, "TIPO": tipo}}, {"$sample": {"size": 1}}]))

    if not q_list:
        msg = "Não achei mais questões desse tipo. Mude o assunto no /start!"
        if hasattr(update_or_query, 'edit_message_text'): await update_or_query.edit_message_text(msg)
        else: await update_or_query.message.reply_text(msg)
        return

    q = q_list[0]
    texto_q = f"📝 <b>{q.get('TIPO', 'Questão')}</b> | <b>Assunto:</b> {q.get('CONTEUDO')}\n\n"
    
    # --- FILTRO DE PROTEÇÃO HTML (Evita quebrar com matemática) ---
    pergunta_limpa = str(q.get('PERGUNTA', '')).replace('<', '&lt;').replace('>', '&gt;')
    texto_q += f"{pergunta_limpa}\n\n"
    
    for letra in ["A", "B", "C", "D"]:
        opcao_limpa = str(q.get(letra, '')).replace('<', '&lt;').replace('>', '&gt;')
        texto_q += f"<b>{letra})</b> {opcao_limpa}\n"
    # --------------------------------------------------------------
    
    texto_q += "\n✍️ <i>Mande apenas a letra da resposta correta:</i>"

    colecao_hist.update_one(
        {"user_id": user_id}, 
        {"$set": {"questao_ativa": q, "ultimo_texto_bot": texto_q}, "$push": {"questoes_vistas": q["_id"]}}, 
        upsert=True
    )

    if hasattr(update_or_query, 'edit_message_text'):
        await update_or_query.edit_message_text(texto_q, reply_markup=ui.teclado_parar(), parse_mode="HTML")
    else:
        await update_or_query.reply_text(texto_q, reply_markup=ui.teclado_parar(), parse_mode="HTML")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not update.message or not update.message.text: return
    
    texto_entrada = update.message.text.strip()
    
    letras_encontradas = re.findall(r'\b([A-Da-d])\b', texto_entrada)
    
    if letras_encontradas:
        texto_upper = letras_encontradas[-1].upper()
    else:
        texto_upper = texto_entrada.upper()
    
    doc_usuario = colecao_hist.find_one({"user_id": user_id}) or {}
    questao_ativa = doc_usuario.get("questao_ativa")

    if questao_ativa and texto_upper in ["A", "B", "C", "D"]:
        correta = str(questao_ativa.get("CORRETA", "")).upper()
        tema_atual = doc_usuario.get("tema_atual")
        tipo_atual = doc_usuario.get("tipo_atual")
        
        feedback = "✨ <b>BOA! Você acertou.</b>\n\n" if texto_upper == correta else f"⚠️ <b>Não foi dessa vez.</b> A correta era a <b>{correta}</b>.\n\n"
        feedback += "🔎 <b>Análise das alternativas:</b>\n"
        
        for letra in ["A", "B", "C", "D"]:
            # Filtro de proteção HTML nas explicações também
            explica = str(questao_ativa.get(f"COM_{letra}", "Sem explicação disponível.")).replace('<', '&lt;').replace('>', '&gt;')
            status = "✅" if letra == correta else "❌"
            feedback += f"{status} <b>{letra}:</b> {explica}\n"
        
        colecao_hist.update_one(
            {"user_id": user_id}, 
            {"$set": {"ultima_entrada_usuario": texto_upper, "ultimo_feedback_completo": feedback}}
        )
        
        await update.message.reply_text(feedback, reply_markup=ui.teclado_likert(), parse_mode="HTML")
        await asyncio.sleep(2.0)
        await enviar_questao(update.message, context, user_id, tema_atual, tipo_atual)
    
    else:
        nome = update.effective_user.first_name
        await update.message.reply_text(
            f"Opa, {nome}! 🎓 Bora praticar um pouco? Escolha uma matéria abaixo:",
            reply_markup=ui.teclado_materias()
        )

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("limpar", limpar))
    app.add_handler(CallbackQueryHandler(callback_handler)) 
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    print("O Bot está rodando! 🚀")
    app.run_polling()