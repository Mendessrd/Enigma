import os
import bcrypt
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ==============================
# USUÁRIOS
# ==============================
def cadastrar(usuario, senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    data = {
        "usuario": usuario,
        "senha": senha_hash,
        "pontos": 0
    }

    res = supabase.table("usuarios").insert(data).execute()
    return res.data is not None


def login(usuario, senha):
    res = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()

    if res.data:
        user = res.data[0]
        if bcrypt.checkpw(senha.encode(), user["senha"].encode()):
            return user["id"]

    return None


def adicionar_pontos(user_id, pontos):
    user = supabase.table("usuarios").select("pontos").eq("id", user_id).execute()

    if not user.data:
        return False

    total = user.data[0]["pontos"] + pontos

    supabase.table("usuarios").update({
        "pontos": total
    }).eq("id", user_id).execute()

    return True


def obter_usuario(user_id):
    res = supabase.table("usuarios").select("*").eq("id", user_id).execute()

    if res.data:
        return res.data[0]

    return None
