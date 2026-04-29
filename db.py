import streamlit as st
import bcrypt
from supabase import create_client
import random

# =========================
# SUPABASE
# =========================
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# USUÁRIOS
# =========================
def cadastrar(usuario, senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    return supabase.table("usuarios").insert({
        "usuario": usuario,
        "senha": senha_hash,
        "pontos": 0,
        "admin": False
    }).execute().data


def login(usuario, senha):
    try:
        res = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

    if res.data:
        user = res.data[0]

        if bcrypt.checkpw(senha.encode(), user["senha"].encode()):
            return user["id"]

    return None


def obter_usuario(user_id):
    res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None


def adicionar_pontos(user_id, pontos):
    user = obter_usuario(user_id)

    if not user:
        return

    novo = user["pontos"] + pontos

    supabase.table("usuarios") \
        .update({"pontos": novo}) \
        .eq("id", user_id) \
        .execute()


# =========================
# ENIGMAS
# =========================
def criar_enigma(pergunta, resposta, dicas, dificuldade, pontos):
    return supabase.table("enigmas").insert({
        "pergunta": pergunta,
        "resposta": resposta,
        "dicas": dicas,
        "dificuldade": dificuldade,
        "pontos": pontos
    }).execute().data


def listar_enigmas_disponiveis(user_id, dificuldade="todos"):
    query = supabase.table("enigmas").select("*")

    if dificuldade != "todos":
        query = query.eq("dificuldade", dificuldade)

    enigmas = query.execute().data

    tentativas = supabase.table("tentativas") \
        .select("enigma_id, concluido") \
        .eq("usuario_id", user_id) \
        .execute().data

    concluidos = {t["enigma_id"] for t in tentativas if t["concluido"]}

    return [e for e in enigmas if e["id"] not in concluidos]


def listar_enigmas_resolvidos(user_id):
    tentativas = supabase.table("tentativas") \
        .select("enigma_id") \
        .eq("usuario_id", user_id) \
        .eq("concluido", True) \
        .execute().data

    if not tentativas:
        return []

    ids = [t["enigma_id"] for t in tentativas]

    enigmas = supabase.table("enigmas") \
        .select("*") \
        .in_("id", ids) \
        .execute().data

    return enigmas


# =========================
# TENTATIVAS
# =========================
def get_status(user_id, enigma_id):
    res = supabase.table("tentativas") \
        .select("*") \
        .eq("usuario_id", user_id) \
        .eq("enigma_id", enigma_id) \
        .execute()

    return res.data[0] if res.data else None


def registrar_tentativa(user_id, enigma_id):
    status = get_status(user_id, enigma_id)

    if not status:
        supabase.table("tentativas").insert({
            "usuario_id": user_id,
            "enigma_id": enigma_id,
            "tentativas": 1,
            "concluido": False
        }).execute()
        return 1, False

    if status["concluido"]:
        return status["tentativas"], True

    tent = status["tentativas"] + 1
    done = tent >= 3

    supabase.table("tentativas") \
        .update({
            "tentativas": tent,
            "concluido": done
        }) \
        .eq("id", status["id"]) \
        .execute()

    return tent, done


def marcar_concluido(user_id, enigma_id):
    supabase.table("tentativas").upsert({
        "usuario_id": user_id,
        "enigma_id": enigma_id,
        "concluido": True,
        "tentativas": 3
    }).execute()


# =========================
# RANKING
# =========================
def ranking():
    return supabase.table("usuarios") \
        .select("*") \
        .eq("admin", False) \
        .order("pontos", desc=True) \
        .execute().data
