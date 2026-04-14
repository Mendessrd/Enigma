import streamlit as st
from db import *

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Enigmas Game", layout="centered")

# =========================
# CSS (UI GAME)
# =========================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid #1f2937;
}

/* Títulos */
h1, h2, h3 {
    color: #00e5ff !important;
    text-shadow: 0px 0px 10px #00e5ff55;
}

/* Botões */
.stButton button {
    background: linear-gradient(90deg, #00e5ff, #7c3aed);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.6rem 1rem;
    font-weight: bold;
}

.stButton button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 15px #00e5ff88;
}

/* Inputs */
input, textarea {
    background-color: #0b1220 !important;
    color: white !important;
    border: 1px solid #1f2937 !important;
    border-radius: 8px !important;
}

/* Card */
.game-card {
    background: #0b1220;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #1f2937;
    margin-bottom: 20px;
}

.glow {
    color: #00e5ff;
    text-shadow: 0 0 10px #00e5ff;
}

</style>
""", unsafe_allow_html=True)

# =========================
# ADMIN FIXO
# =========================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# =========================
# LOGOUT
# =========================
def logout():
    for key in ["user_id", "enigma", "dica_index", "pontos_atual", "admin"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# =========================
# SIDEBAR HUD (TOPO)
# =========================
st.sidebar.markdown("## 🎮 PLAYER HUD")

if "user_id" in st.session_state:
    user = obter_usuario(st.session_state["user_id"])

    st.sidebar.markdown(f"""
    <div style="
        padding:12px;
        background:#0b1220;
        border-radius:12px;
        border:1px solid #1f2937;
        margin-bottom:15px;
    ">
        👤 <b>{user['usuario']}</b><br>
        ⭐ Pontos: <b>{user['pontos']}</b>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Sair"):
        logout()

else:
    st.sidebar.markdown("""
    <div style="
        padding:12px;
        background:#0b1220;
        border-radius:12px;
        border:1px solid #1f2937;
        margin-bottom:15px;
    ">
        ❌ Não logado
    </div>
    """, unsafe_allow_html=True)

# =========================
# MENU
# =========================
menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Cadastro", "Jogar", "Admin", "Ranking"]
)

st.title("🧩 Enigmas Game")

st.sidebar.divider()

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
        e = pegar_enigma_aleatorio()

        if not e:
            st.error("Nenhum enigma cadastrado")
            st.stop()

        st.session_state["enigma"] = e
        st.session_state["dica_index"] = 0
        st.session_state["pontos_atual"] = e["pontos"]

    e = st.session_state["enigma"]

    # CARD ENIGMA
    st.markdown(f"""
    <div class="game-card">
        <h2 class="glow">🧩 Enigma</h2>
        <p style="font-size:18px">{e['pergunta']}</p>
    </div>
    """, unsafe_allow_html=True)

    # DICAS
    if st.button("💡 Mostrar dica"):

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

    # STATUS
    status = get_status(st.session_state["user_id"], e["id"])

    if status and status["concluido"]:
        st.error("Você já concluiu este enigma")
        st.stop()

    resposta = st.text_input("Sua resposta")

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

        st.subheader("🧩 Criar Enigma")

        pergunta = st.text_area("Pergunta")
        resposta = st.text_input("Resposta")
        dicas_input = st.text_area("Dicas (uma por linha)")

        dificuldade = st.selectbox("Dificuldade", ["fácil", "médio", "difícil"])
        pontos = st.number_input("Pontos", 1, 100, 10)

        if st.button("Criar"):

            dicas = [d.strip() for d in dicas_input.split("\n") if d.strip()]

            criar_enigma(pergunta, resposta, dicas, dificuldade, pontos)

            st.success("Enigma criado!")

# =========================
# RANKING
# =========================
elif menu == "Ranking":

    st.title("🏆 Ranking Global")

    for u in ranking():
        st.write(f"👤 {u['usuario']} — ⭐ {u['pontos']} pts")