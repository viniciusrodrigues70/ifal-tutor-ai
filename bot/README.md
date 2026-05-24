# 🎓 TutorBot AI - Projeto de Pesquisa IFAL

Este repositório contém o código-fonte de um chatbot inteligente desenvolvido para o **Instituto Federal de Alagoas (IFAL)**. O projeto faz parte de uma pesquisa acadêmica que investiga o impacto do uso de Inteligência Artificial no engajamento e desempenho de estudantes do Ensino Médio.

## 🔬 Sobre a Pesquisa

O objetivo central deste bot é testar a hipótese: **"Perguntas geradas e mediadas por IA podem ajudar estudantes do Ensino Médio a aprimorar seus conhecimentos através de quizzes interativos?"**

O bot atua como um tutor 24/7, oferecendo:
- Questões categorizadas por matéria, conteúdo e nível de dificuldade.
- Feedback imediato com análise detalhada de alternativas (justificativa de erro/acerto).
- Sistema de avaliação de utilidade (Escala Likert) para coleta de dados da pesquisa.

## 👨‍🏫 Orientação
- **Orientador:** Prof. Elvys Soares
- **Instituição:** Instituto Federal de Alagoas (IFAL)

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** [Python 3.10+](https://www.python.org/)
- **Framework:** [python-telegram-bot](https://python-telegram-bot.org/) (Interface do usuário)
- **Banco de Dados:** [MongoDB Atlas](https://www.mongodb.com/) (Armazenamento de questões e logs de interação)
- **Segurança:** Variáveis de ambiente com `python-dotenv`
- **Estrutura:** Arquitetura Modular (SoC - Separation of Concerns)

## 📂 Estrutura do Projeto
```text
bot/
├── main.py       # Cérebro do bot e handlers de mensagens
├── config.py     # Gerenciamento de conexões e variáveis de ambiente
├── ui.py         # Interface de teclados e menus dinâmicos
├── utils.py      # Funções utilitárias e persistência local
└── .env          # Variáveis sensíveis (não incluído no repositório)