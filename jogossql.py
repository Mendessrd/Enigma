import os
import bcrypt
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# ==============================
# CONFIGURAÇÃO
# ==============================
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# ==============================
# USUÁRIOS
# ==============================

def cadastrar(usuario, senha, admin=False):
    try:
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

        data = {
            "usuario": usuario,
            "senha": senha_hash,
            "pontos": 0,
            "admin": admin
        }

        response = supabase.table("usuarios").insert(data).execute()
        return response.data is not None

    except Exception as e:
        print("Erro ao cadastrar:", e)
        return False


def login(usuario, senha):
    try:
        response = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()

        if response.data:
            user = response.data[0]

            if bcrypt.checkpw(senha.encode(), user["senha"].encode()):
                return user["id"], user["admin"]

        return None

    except Exception as e:
        print("Erro no login:", e)
        return None


def obter_info_usuario(usuario_id):
    try:
        response = supabase.table("usuarios").select("*").eq("id", usuario_id).execute()

        if response.data:
            user = response.data[0]
            return user["usuario"], user["pontos"], user["admin"]

        return None

    except Exception as e:
        print("Erro ao obter usuário:", e)
        return None


def adicionar_pontos(usuario_id, pontos):
    try:
        user = supabase.table("usuarios").select("pontos").eq("id", usuario_id).execute()

        if not user.data:
            return False

        pontos_atual = user.data[0]["pontos"]

        response = supabase.table("usuarios").update({
            "pontos": pontos_atual + pontos
        }).eq("id", usuario_id).execute()

        return response.data is not None

    except Exception as e:
        print("Erro ao adicionar pontos:", e)
        return False


# ==============================
# ENIGMAS
# ==============================

def listar_enigmas(dificuldade):
    try:
        response = supabase.table("enigmas").select("*").eq("dificuldade", dificuldade).execute()
        return response.data or []

    except Exception as e:
        print("Erro ao listar enigmas:", e)
        return []


def obter_dicas(enigma_id):
    try:
        response = supabase.table("dicas").select("dica").eq("enigma_id", enigma_id).execute()
        return [d["dica"] for d in response.data] if response.data else []

    except Exception as e:
        print("Erro ao obter dicas:", e)
        return []


# ==============================
# TENTATIVAS
# ==============================

def obter_tentativas(usuario_id, enigma_id):
    try:
        response = supabase.table("tentativas_usuario") \
            .select("*") \
            .eq("usuario_id", usuario_id) \
            .eq("enigma_id", enigma_id) \
            .execute()

        if not response.data:
            data = {
                "usuario_id": usuario_id,
                "enigma_id": enigma_id,
                "tentativas_restantes": 3
            }

            supabase.table("tentativas_usuario").insert(data).execute()
            return 3

        return response.data[0]["tentativas_restantes"]

    except Exception as e:
        print("Erro ao obter tentativas:", e)
        return 0


def decrementar_tentativa(usuario_id, enigma_id):
    try:
        response = supabase.table("tentativas_usuario") \
            .select("tentativas_restantes") \
            .eq("usuario_id", usuario_id) \
            .eq("enigma_id", enigma_id) \
            .execute()

        if not response.data:
            return False

        atual = response.data[0]["tentativas_restantes"]
        novo_valor = max(atual - 1, 0)

        update = supabase.table("tentativas_usuario").update({
            "tentativas_restantes": novo_valor
        }).eq("usuario_id", usuario_id).eq("enigma_id", enigma_id).execute()

        return update.data is not None

    except Exception as e:
        print("Erro ao decrementar tentativa:", e)
        return False


# ==============================
# CONCLUSÃO
# ==============================

def enigma_concluido(usuario_id, enigma_id):
    try:
        response = supabase.table("enigmas_respondidos") \
            .select("*") \
            .eq("usuario_id", usuario_id) \
            .eq("enigma_id", enigma_id) \
            .execute()

        return bool(response.data and response.data[0]["concluido"])

    except Exception as e:
        print("Erro ao verificar conclusão:", e)
        return False


def marcar_concluido(usuario_id, enigma_id):
    try:
        data = {
            "usuario_id": usuario_id,
            "enigma_id": enigma_id,
            "concluido": True
        }

        response = supabase.table("enigmas_respondidos").upsert(data).execute()
        return response.data is not None

    except Exception as e:
        print("Erro ao marcar concluído:", e)
        return False