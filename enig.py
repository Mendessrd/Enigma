import streamlit as st
from db import cadastrar, login, adicionar_pontos, obter_usuario
from ia import gerar_enigma, validar_resposta

st.set_page_config(page_title="Jogo de Enigmas", layout="centered")

st.title("🧩 Enigmas com IA")

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro", "Jogar"])

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
            enigma, resposta, dica = gerar_enigma()

            st.session_state["enigma"] = enigma
            st.session_state["resposta"] = resposta
            st.session_state["dica"] = dica

        st.subheader("🧩 Enigma")
        st.write(st.session_state["enigma"])

        if st.button("Mostrar dica"):
            st.info(st.session_state["dica"])

        resposta_user = st.text_input("Sua resposta")

        if st.button("Responder"):
            correto = validar_resposta(
                resposta_user,
                st.session_state["resposta"]
            )

            if correto:
                st.success("✅ Correto!")
                adicionar_pontos(st.session_state["user_id"], 10)

                # novo enigma
                del st.session_state["enigma"]

            else:
                st.error("❌ Errado")

        user = obter_usuario(st.session_state["user_id"])
        st.write(f"⭐ Pontos: {user['pontos']}")
