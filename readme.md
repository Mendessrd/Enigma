# 🧩 Enigmas Game

Uma plataforma interativa de enigmas estilo jogo, onde usuários resolvem desafios, acumulam pontos e competem em um ranking global.

---

## 🎮 Funcionalidades

- 🔐 Login e cadastro de usuários
- 👤 Sistema de perfil com pontuação
- 🧩 Seleção de enigmas por dificuldade
- 💡 Dicas progressivas (cada dica reduz pontos)
- ⚔️ Limite de 3 tentativas por enigma
- 🏆 Ranking global (admin não participa)
- 🧑‍💻 Painel admin para criação de enigmas
- 📊 Controle de enigmas concluídos

---

## 🧠 Como funciona

Cada enigma possui:

- Pergunta
- Resposta
- Dicas (múltiplas)
- Dificuldade (fácil, médio, difícil)
- Pontuação base

O jogador:
- escolhe um enigma
- pode usar dicas (perdendo pontos)
- tem até 3 tentativas
- ganha pontos ao acertar

---

## 🛠️ Tecnologias

- Python
- Streamlit
- Supabase (PostgreSQL)
- bcrypt

---

## 🚀 Instalação

```bash
git clone https://github.com/Mendessrd/Enigma
cd enigma
pip install -r requirements.txt
