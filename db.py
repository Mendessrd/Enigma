import streamlit as st
import bcrypt
from supabase import create_client

# ==============================
# CONEXÃO SUPABASE
# ==============================
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ==============================
# USUÁRIOS
# ==============================

def cadastrar(usuario, senha):
    senha_hash = bcrypt.hashpw(
        senha.encode(),
        bcrypt.gensalt()
    ).decode()

    data = {
        "usuario": usuario,
        "senha": senha_hash,
        "pontos": 0
    }

    res = supabase.table("usuarios").insert(data).execute()
    return res.data is not None


def login(usuario, senha):
    res = (
        supabase.table("usuarios")
        .select("*")
        .eq("usuario", usuario)
        .execute()
    )

    if res.data:
        user = res.data[0]

        if bcrypt.checkpw(
            senha.encode(),
            user["senha"].encode()
        ):
            return user["id"]

    return None


def adicionar_pontos(user_id, pontos):
    res = (
        supabase.table("usuarios")
        .select("pontos")
        .eq("id", user_id)
        .execute()
    )

    if not res.data:
        return False

    total = res.data[0]["pontos"] + pontos

    supabase.table("usuarios").update({
        "pontos": total
    }).eq("id", user_id).execute()

    return True


def obter_usuario(user_id):
    res = (
        supabase.table("usuarios")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if res.data:
        return res.data[0]

    return None
