import streamlit as st
from db_functions import *

# Streamlit UI
st.set_page_config(page_title="Sistema de Enigmas", layout="centered")
st.title("Enigmas do Taijara")

# MENU
menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro", "Jogar", "Ranking"])


# CADASTRO
if menu == "Cadastro":
    st.subheader("Criar conta")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        if user and senha:
            if cadastrar(user, senha):
                st.success("Conta criada com sucesso!")
            else:
                st.error("Usuário já existe!")
        else:
            st.warning("Preencha todos os campos")


# LOGIN
elif menu == "Login":
    st.subheader("Entrar")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Login"):
        dados = login(user, senha)
        if dados:
            st.session_state["user_id"] = dados[0]
            st.session_state["admin"] = dados[1]
            st.success("Login realizado!")
            # Mostra info do usuário após login
            info = obter_info_usuario(dados[0])
            st.info(
                f"👤 Usuário: {info[0]}\n"
                f"⭐ Pontos: {info[1]}\n"
            )
        else:
            st.error("Credenciais inválidas")


# JOGAR
elif menu == "Jogar":
    if "user_id" not in st.session_state:
        st.warning("Faça login primeiro!")
    else:
        st.subheader("🎮 Jogar")
        usuario_id = st.session_state["user_id"]

        dificuldade = st.selectbox("Escolha a dificuldade", ["Fácil", "Médio", "Difícil"])
        enigmas = listar_enigmas(dificuldade)

        if enigmas:
            opcoes = {f"{e['id']} - {e['pergunta'][:50]}...": e for e in enigmas}
            escolha = st.selectbox("Escolha o enigma", list(opcoes.keys()))

            if escolha:
                enigma = opcoes[escolha]
                enigma_id = enigma["id"]
                pergunta = enigma["pergunta"]
                resposta_correta = enigma["resposta"].lower().strip()
                pontos_iniciais = enigma["pontos"]

                # Verifica se já concluiu
                if enigma_concluido(usuario_id, enigma_id):
                    st.success("✅ Você já concluiu este enigma e não pode responder novamente!")
                else:
                    tentativas_restantes = obter_tentativas(usuario_id, enigma_id)
                    dicas = obter_dicas(enigma_id)

                    if "dica_index" not in st.session_state or st.session_state.get("enigma_atual") != enigma_id:
                        st.session_state["dica_index"] = 0
                        st.session_state["enigma_atual"] = enigma_id
                        st.session_state["pontos_restantes"] = pontos_iniciais

                    st.write("🧩 Pergunta:")
                    st.info(pergunta)

                    if tentativas_restantes <= 0:
                        st.warning("Você esgotou todas as tentativas!")
                        marcar_concluido(usuario_id, enigma_id)
                   
