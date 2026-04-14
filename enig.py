import streamlit as st
from db import *

st.set_page_config(page_title="Enigmas Game", layout="centered")

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro", "Jogar", "Admin", "Ranking"])

# =========================
# CADASTRO
# =========================
if menu == "Cadastro":
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        cadastrar(user, senha)
        st.success("Criado!")

# =========================
# LOGIN
# =========================
elif menu == "Login":
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        uid = login(user, senha)
        if uid:
            st.session_state["user_id"] = uid
            st.success("Logado!")

# =========================
# JOGO
# =========================
elif menu == "Jogar":

    if "user_id" not in st.session_state:
        st.warning("Faça login")
        st.stop()

    if "enigma" not in st.session_state:
        st.session_state["enigma"] = pegar_enigma_aleatorio()
        st.session_state["dica_index"] = 0
        st.session_state["pontos_atual"] = st.session_state["enigma"]["pontos"]

    e = st.session_state["enigma"]

    st.title(e["pergunta"])

    # =========================
    # DICAS PROGRESSIVAS
    # =========================
    if st.button("Mostrar dica"):

        dicas = e.get("dicas", [])

        if st.session_state["dica_index"] < len(dicas):

            st.info(dicas[st.session_state["dica_index"]])
            st.session_state["dica_index"] += 1

            st.session_state["pontos_atual"] = max(
                0,
                st.session_state["pontos_atual"] - 5
            )

        else:
            st.warning("Sem mais dicas")

    st.write(f"⭐ Pontos atuais: {st.session_state['pontos_atual']}")

    status = get_status(st.session_state["user_id"], e["id"])

    if status and status["concluido"]:
        st.error("Você já concluiu este enigma")
        st.stop()

    resposta = st.text_input("Resposta")

    if st.button("Responder"):

        tent, done = registrar_tentativa(
            st.session_state["user_id"],
            e["id"]
        )

        if resposta.strip().lower() == e["resposta"].strip().lower():

            st.success("Correto!")

            adicionar_pontos(
                st.session_state["user_id"],
                st.session_state["pontos_atual"]
            )

            marcar_concluido(st.session_state["user_id"], e["id"])

            del st.session_state["enigma"]
            del st.session_state["dica_index"]
            del st.session_state["pontos_atual"]

        else:

            if done:
                st.error("3 tentativas atingidas")
            else:
                st.error(f"Errado ({tent}/3)")

# =========================
# ADMIN
# =========================
elif menu == "Admin":

    if "admin" not in st.session_state:

        u = st.text_input("Admin")
        p = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state["admin"] = True
                st.success("OK")

    else:

        st.subheader("Criar Enigma")

        pergunta = st.text_area("Pergunta")
        resposta = st.text_input("Resposta")
        dicas_input = st.text_area("Dicas (uma por linha)")

        dificuldade = st.selectbox("Dificuldade", ["fácil", "médio", "difícil"])
        pontos = st.number_input("Pontos", 1, 100, 10)

        if st.button("Criar"):

            dicas = [d.strip() for d in dicas_input.split("\n") if d.strip()]

            criar_enigma(pergunta, resposta, dicas, dificuldade, pontos)

            st.success("Criado!")

# =========================
# RANKING
# =========================
elif menu == "Ranking":

    st.title("🏆 Ranking Global")

    for u in ranking():
        st.write(f"{u['usuario']} - {u['pontos']} pts")