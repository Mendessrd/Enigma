import streamlit as st
import sqlite3

DB = "jogo.db"



def conectar():
    return sqlite3.connect(DB, check_same_thread=False)

conn = conectar()
cursor = conn.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    usuario TEXT PRIMARY KEY,
    senha TEXT,
    pontos INTEGER DEFAULT 0,
    admin INTEGER DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS enigmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pergunta TEXT,
    resposta TEXT,
    dificuldade TEXT,
    pontos INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS dicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enigma_id INTEGER,
    dica TEXT,
    FOREIGN KEY(enigma_id) REFERENCES enigmas(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS tentativas_usuario (
    usuario TEXT,
    enigma_id INTEGER,
    tentativas_restantes INTEGER DEFAULT 3,
    PRIMARY KEY (usuario, enigma_id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS enigmas_respondidos (
    usuario TEXT,
    enigma_id INTEGER,
    concluido INTEGER DEFAULT 0,
    PRIMARY KEY(usuario, enigma_id)
)
""")
conn.commit()



def cadastrar(usuario, senha, admin=0):
    try:
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, pontos, admin) VALUES (?, ?, 0, ?)",
            (usuario, senha, admin)
        )
        conn.commit()
        return True
    except:
        return False

def login(usuario, senha):
    cursor.execute(
        "SELECT usuario, admin FROM usuarios WHERE usuario=? AND senha=?",
        (usuario, senha)
    )
    return cursor.fetchone()

def adicionar_pontos(usuario, pontos):
    cursor.execute(
        "UPDATE usuarios SET pontos = pontos + ? WHERE usuario=?",
        (pontos, usuario)
    )
    conn.commit()

def obter_info_usuario(usuario):
    cursor.execute(
        "SELECT usuario, pontos, admin FROM usuarios WHERE usuario=?",
        (usuario,)
    )
    return cursor.fetchone()  




def listar_enigmas(dificuldade):
    cursor.execute(
        "SELECT id, pergunta, pontos, resposta FROM enigmas WHERE dificuldade=?",
        (dificuldade,)
    )
    return cursor.fetchall()

def obter_dicas(enigma_id):
    cursor.execute(
        "SELECT dica FROM dicas WHERE enigma_id=? ORDER BY id",
        (enigma_id,)
    )
    return [row[0] for row in cursor.fetchall()]

def obter_tentativas(usuario, enigma_id):
    cursor.execute(
        "SELECT tentativas_restantes FROM tentativas_usuario WHERE usuario=? AND enigma_id=?",
        (usuario, enigma_id)
    )
    resultado = cursor.fetchone()
    if resultado is None:
        cursor.execute(
            "INSERT INTO tentativas_usuario (usuario, enigma_id, tentativas_restantes) VALUES (?, ?, 3)",
            (usuario, enigma_id)
        )
        conn.commit()
        return 3
    return resultado[0]

def decrementar_tentativa(usuario, enigma_id):
    cursor.execute(
        "UPDATE tentativas_usuario SET tentativas_restantes = tentativas_restantes - 1 WHERE usuario=? AND enigma_id=?",
        (usuario, enigma_id)
    )
    conn.commit()

def enigma_concluido(usuario, enigma_id):
    cursor.execute(
        "SELECT concluido FROM enigmas_respondidos WHERE usuario=? AND enigma_id=?",
        (usuario, enigma_id)
    )
    resultado = cursor.fetchone()
    return resultado is not None and resultado[0] == 1

def marcar_concluido(usuario, enigma_id):
    cursor.execute(
        "INSERT OR REPLACE INTO enigmas_respondidos (usuario, enigma_id, concluido) VALUES (?, ?, 1)",
        (usuario, enigma_id)
    )
    conn.commit()



st.set_page_config(page_title="Sistema de Enigmas", layout="centered")
st.title("Enigmas do Taijara")


# BARRA LATERAL COM INFORMAÇÕES DO USUÁRIO
st.sidebar.title("👤 Perfil do Jogador")
if "user" in st.session_state:
    info = obter_info_usuario(st.session_state["user"])
    st.sidebar.markdown(f"**Usuário:** {info[0]}")
    st.sidebar.markdown(f"**Pontos:** {info[1]}")
    st.sidebar.markdown(f"**Admin:** {'Sim' if info[2]==1 else 'Não'}")
else:
    st.sidebar.markdown("Faça login para ver suas informações")


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
            st.session_state["user"] = dados[0]
            st.success("Login realizado!")
            # Mostra info do usuário após login
            info = obter_info_usuario(user)
            st.info(
                f"👤 Usuário: {info[0]}\n"
                f"⭐ Pontos: {info[1]}\n"
            )
        else:
            st.error("Credenciais inválidas")


# JOGAR
elif menu == "Jogar":
    if "user" not in st.session_state:
        st.warning("Faça login primeiro!")
    else:
        st.subheader("🎮 Jogar")
        usuario = st.session_state["user"]

        dificuldade = st.selectbox("Escolha a dificuldade", ["Fácil", "Médio", "Difícil"])
        enigmas = listar_enigmas(dificuldade)

        if enigmas:
            opcoes = {f"{e[0]} - {e[1][:50]}...": e for e in enigmas}
            escolha = st.selectbox("Escolha o enigma", list(opcoes.keys()))

            if escolha:
                enigma = opcoes[escolha]
                enigma_id = enigma[0]
                pergunta = enigma[1]
                resposta_correta = enigma[3].lower().strip()
                pontos_iniciais = enigma[2]

                # Verifica se já concluiu
                if enigma_concluido(usuario, enigma_id):
                    st.success("✅ Você já concluiu este enigma e não pode responder novamente!")
                else:
                    tentativas_restantes = obter_tentativas(usuario, enigma_id)
                    dicas = obter_dicas(enigma_id)

                    if "dica_index" not in st.session_state or st.session_state.get("enigma_atual") != enigma_id:
                        st.session_state["dica_index"] = 0
                        st.session_state["enigma_atual"] = enigma_id
                        st.session_state["pontos_restantes"] = pontos_iniciais

                    st.write("🧩 Pergunta:")
                    st.info(pergunta)

                    if tentativas_restantes <= 0:
                        st.warning("Você esgotou todas as tentativas!")
                        marcar_concluido(usuario, enigma_id)
                    else:
                        resposta = st.text_input("Sua resposta")
                        if st.button("Responder"):
                            if resposta.lower().strip() == resposta_correta:
                                adicionar_pontos(usuario, st.session_state["pontos_restantes"])
                                st.success(f"✅ Correto! +{st.session_state['pontos_restantes']} pontos")
                                marcar_concluido(usuario, enigma_id)
                            else:
                                st.error("❌ Resposta errada!")
                                decrementar_tentativa(usuario, enigma_id)
                                tentativas_restantes -= 1
                                if tentativas_restantes == 0:
                                    st.warning("Você esgotou todas as tentativas!")
                                    marcar_concluido(usuario, enigma_id)
                            st.session_state["dica_index"] = 0
                            st.session_state["pontos_restantes"] = pontos_iniciais

                        # Mostrar dicas
                        if st.session_state["dica_index"] < len(dicas):
                            if st.button("Mostrar dica"):
                                st.session_state["dica_index"] += 1
                                st.session_state["pontos_restantes"] = max(0, st.session_state["pontos_restantes"] - 5)

                        # Mostrar dicas já exibidas
                        for i in range(st.session_state["dica_index"]):
                            st.info(f"Dica {i+1}: {dicas[i]}")

                        st.write(f"🔸 Pontos atuais do enigma: {st.session_state['pontos_restantes']}")
                        st.write(f"🔹 Tentativas restantes: {tentativas_restantes}")
        else:
            st.info("Nenhum enigma disponível nessa dificuldade.")


# RANKING
elif menu == "Ranking":
    st.subheader("🏆 Ranking")
    cursor.execute("SELECT usuario, pontos FROM usuarios ORDER BY pontos DESC")
    ranking = cursor.fetchall()
    if ranking:
        for i, (user, pontos) in enumerate(ranking, start=1):
            st.write(f"{i}º - {user}: {pontos} pontos")
    else:
        st.info("Nenhum jogador ainda.")