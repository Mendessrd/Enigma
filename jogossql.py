from supabase import create_client, Client

# Configuração do Supabase
url = "https://YOUR_PROJECT_URL.supabase.co"  # Substitua com sua URL do Supabase
key = "YOUR_API_KEY"  # Substitua com sua chave de API
supabase: Client = create_client(url, key)

# Função para criar tabelas (Isso é feito no painel do Supabase, não necessário aqui)
def criar_tabelas():
    pass

# Funções relacionadas a usuários
def cadastrar(usuario, senha, admin=0):
    data = {"usuario": usuario, "senha": senha, "pontos": 0, "admin": admin}
    try:
        response = supabase.table("usuarios").insert(data).execute()
        if response.status_code == 201:
            return True
    except Exception as e:
        print(f"Erro ao cadastrar: {e}")
    return False


def login(usuario, senha):
    response = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("senha", senha).execute()
    if response.data:
        return response.data[0]["usuario"], response.data[0]["admin"]
    return None


def adicionar_pontos(usuario, pontos):
    response = supabase.table("usuarios").update({"pontos": {"pontos": pontos}}).eq("usuario", usuario).execute()
    return response.status_code == 200


def obter_info_usuario(usuario):
    response = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
    if response.data:
        return response.data[0]["usuario"], response.data[0]["pontos"], response.data[0]["admin"]
    return None


# Funções relacionadas aos enigmas
def listar_enigmas(dificuldade):
    response = supabase.table("enigmas").select("*").eq("dificuldade", dificuldade).execute()
    return response.data


def obter_dicas(enigma_id):
    response = supabase.table("dicas").select("dica").eq("enigma_id", enigma_id).execute()
    return [dica["dica"] for dica in response.data]


def obter_tentativas(usuario, enigma_id):
    response = supabase.table("tentativas_usuario").select("*").eq("usuario", usuario).eq("enigma_id", enigma_id).execute()
    if not response.data:
        data = {"usuario": usuario, "enigma_id": enigma_id, "tentativas_restantes": 3}
        supabase.table("tentativas_usuario").insert(data).execute()
        return 3
    return response.data[0]["tentativas_restantes"]


def decrementar_tentativa(usuario, enigma_id):
    response = supabase.table("tentativas_usuario").update({"tentativas_restantes": {"tentativas_restantes": -1}}).eq("usuario", usuario).eq("enigma_id", enigma_id).execute()
    return response.status_code == 200


def enigma_concluido(usuario, enigma_id):
    response = supabase.table("enigmas_respondidos").select("*").eq("usuario", usuario).eq("enigma_id", enigma_id).execute()
    return len(response.data) > 0 and response.data[0]["concluido"] == 1


def marcar_concluido(usuario, enigma_id):
    response = supabase.table("enigmas_respondidos").upsert([{"usuario": usuario, "enigma_id": enigma_id, "concluido": 1}]).execute()
    return response.status_code == 200
