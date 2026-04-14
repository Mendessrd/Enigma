import streamlit as st
from db import (
    cadastrar,
    login,
    adicionar_pontos,
    obter_usuario,
    criar_enigma,
    pegar_enigma_aleatorio
)

st.set_page_config(page_title="Jogo de Enigmas", layout="centered")

st.title("🧩 Enigmas")

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro", "Jogar", "Admin"])

# ==============================
# CADASTRO
# ==============================
if menu == "Cadastro":
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        if cadastrar(user, senha):
            st.success("Conta criada!")
        else:
            st.error("Erro ao cadastrar")

# ==============================
# LOGIN
# ==============================
elif menu == "Login":
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        uid = login(user, senha)

        if uid:
            st.session_state["user_id"] = uid
            st.success("Logado!")
        else:
            st.error("Erro no login")

# ==============================
# JOGO
# ==============================
elif menu == "Jogar":

    if "user_id" not in st.session_state:
        st.warning("Faça login primeiro")

    else:
        if "enigma" not in st.session_state:
            enigma = pegar_enigma_aleatorio()

            if not enigma:
                st.warning("Nenhum enigma cadastrado")
                st.stop()

            st.session_state["enigma"] = enigma

        e = st.session_state["enigma"]

        st.subheader("🧩 Enigma")
        st.write(e["pergunta"])   # ✅ CORRIGIDO

        if st.button("Mostrar dica"):
            st.info(e["dica"])

        resposta_user = st.text_input("Sua resposta")

        if st.button("Responder"):
            if resposta_user.strip().lower() == e["resposta"].strip().lower():
                st.success("✅ Correto!")

                adicionar_pontos(
                    st.session_state["user_id"],
                    e["pontos"]
                )

                del st.session_state["enigma"]

            else:
                st.error("❌ Errado")

        user = obter_usuario(st.session_state["user_id"])
        st.write(f"⭐ Pontos: {user['pontos']}")

# ==============================
# ADMIN
# ==============================
elif menu == "Admin":

    st.subheader("🔐 Painel Admin - Criar Enigmas")

    pergunta = st.text_area("Enigma")
    resposta = st.text_input("Resposta")
    dica = st.text_input("Dica")

    dificuldade = st.selectbox(
        "Dificuldade",
        ["fácil", "médio", "difícil"]
    )

    pontos = st.number_input("Pontos", min_value=1, value=10)

    if st.button("Criar Enigma"):
        if criar_enigma(pergunta, resposta, dica, dificuldade, pontos):
            st.success("Enigma criado!")
        else:
            st.error("Erro ao criar enigma")