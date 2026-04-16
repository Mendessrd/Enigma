import streamlit as st
from db import *

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Puzzle", layout="centered")

# =========================
# CSS GAME UI
# =========================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: white;
}

[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid #1f2937;
}

h1, h2, h3 {
    color: #00e5ff !important;
    text-shadow: 0px 0px 10px #00e5ff55;
}

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

input, textarea {
    background-color: #0b1220 !important;
    color: white !important;
    border: 1px solid #1f2937 !important;
    border-radius: 8px !important;
}

.game-card {
    background: #0b1220;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #1f2937;
    margin-bottom: 15px;
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
# SIDEBAR HUD
# =========================
st.sidebar.markdown("## Universitários")

if "user_id" in st.session_state:
    user = obter_usuario(st.session_state["user_id"])

    st.sidebar.markdown(f"""
    <div style="padding:12px;background:#0b1220;border-radius:12px;">
        👤 <b>{user['usuario']}</b><br>
        ⭐ {user['pontos']} pontos
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Sair"):
        logout()

else:
    st.sidebar.info("Deslogado")

# =========================
# MENU
# =========================
menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Cadastro", "Jogar", "Admin", "Ranking"]
)

st.title("🧩Puzzle")

st.sidebar.divider()

# =========================
# CADASTRO
# =========================
if menu == "Cadastro":
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        cadastrar(u, s)
        st.success("Criado!")

# =========================
# LOGIN
# =========================
elif menu == "Login":
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        uid = login(u, s)

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

    st.subheader("🎮 Selecionar Enigma")

    dificuldade = st.selectbox("Dificuldade", ["todos", "fácil", "médio", "difícil"])

    enigmas = listar_enigmas(dificuldade)

    if not enigmas:
        st.warning("Nenhum enigma")
        st.stop()

    for e in enigmas:

        st.markdown(f"""
        <div class="game-card">
            🧩 <b>{e['pergunta'][:60]}...</b><br>
            🎯 {e['dificuldade']} | ⭐ {e['pontos']}
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Jogar #{e['id']}"):
            st.session_state["enigma"] = e
            st.session_state["dica_index"] = 0
            st.session_state["pontos_atual"] = e["pontos"]
            st.rerun()

    if "enigma" in st.session_state:

        e = st.session_state["enigma"]

        st.markdown(f"""
        <div class="game-card">
            <h2 class="glow">🧩 {e['pergunta']}</h2>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💡 Mostrar dica"):

            dicas = e.get("dicas", [])

            if st.session_state["dica_index"] < len(dicas):

                st.session_state["dica_index"] += 1

                st.session_state["pontos_atual"] = max(
                    0,
                    st.session_state["pontos_atual"] - 5
                )

        dicas = e.get("dicas", [])

        if dicas:
            st.markdown("### 💡 Dicas desbloqueadas:")

            for i in range(st.session_state["dica_index"]):
                st.markdown(f"""
                <div class="game-card">
                    💡 {dicas[i]}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma dica disponível")

        st.write(f"⭐ Pontos: {st.session_state['pontos_atual']}")

        resposta = st.text_input("Resposta")

        status = get_status(st.session_state["user_id"], e["id"])

        if status and status["concluido"]:
            st.error("Já concluído")
            st.stop()

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

                st.rerun()

            else:
                st.error(f"Errado ({tent}/3)" if not done else "3 tentativas atingidas")

# =========================
# ADMIN
# =========================
elif menu == "Admin":

    if "admin" not in st.session_state:

        st.subheader("🔐 Login Admin")

        u = st.text_input("Admin")
        p = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state["admin"] = True
                st.success("👑 Bem-vindo, administrador!")
                st.toast("Acesso liberado ao painel admin")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

    else:

        st.success("👑 Você está no painel de administrador")
        st.subheader("Criar Enigma")

        p = st.text_area("Pergunta")
        r = st.text_input("Resposta")
        d = st.text_area("Dicas (uma por linha)")
        dif = st.selectbox("Dificuldade", ["fácil", "médio", "difícil"])
        pts = st.number_input("Pontos", 1, 100, 10)

        if st.button("Criar"):

            dicas = [x for x in d.split("\n") if x.strip()]

            criar_enigma(p, r, dicas, dif, pts)

            st.success("Criado!")

# =========================
# RANKING
# =========================
elif menu == "Ranking":

    st.title("🏆 Ranking")

    for u in ranking():
        st.write(f"{u['usuario']} — {u['pontos']} pts")
