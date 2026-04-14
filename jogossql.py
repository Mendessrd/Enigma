from supabase import create_client, Client

# Configuração do Supabase
url = "https://dgluywqmlelrsyranccq.supabase.co"  # Substitua com sua URL do Supabase
key = "sb_publishable_OEWLYDNBKoGB1HRRrWtv8A_tKGZQFR9"  # Substitua com sua chave de API
supabase: Client = create_client(url, key)

# Função para criar tabelas (Isso é feito no painel do Supabase, não necessário aqui)
def cadastrar(usuario, senha, admin=False):
    data = {"usuario": usuario, "senha": senha, "pontos": 0, "admin": admin}
    response = supabase.table("usuarios").insert(data).execute()
    if response.status_code == 201:
        return True
    return False


def login(usuario, senha):
    response = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("senha", senha).execute()
    if response.data:
        return response.data[0]["id"], response.data[0]["admin"]
    return None


def obter_info_usuario(usuario_id):
    response = supabase.table("usuarios").select("*").eq("id", usuario_id).execute()
    if response.data:
        return response.data[0]["usuario"], response.data[0]["pontos"], response.data[0]["admin"]
    return None


def adicionar_pontos(usuario_id, pontos):
    response = supabase.table("usuarios").update({
        "pontos": supabase.raw('pontos + ?', pontos)  # Acumula os pontos
    }).eq("id", usuario_id).execute()
    return response.status_code == 200


# Funções relacionadas aos enigmas
def listar_enigmas(dificuldade):
    response = supabase.table("enigmas").select("*").eq("dificuldade", dificuldade).execute()
    return response.data


def obter_dicas(enigma_id):
    response = supabase.table("dicas").select("dica").eq("enigma_id", enigma_id).execute()
    return [dica["dica"] for dica in response.data]


def obter_tentativas(usuario_id, enigma_id):
    response = supabase.table("tentativas_usuario").select("*").eq("usuario_id", usuario_id).eq("enigma_id", enigma_id).execute()
    if not response.data:
        data = {"usuario_id": usuario_id, "enigma_id": enigma_id, "tentativas_restantes": 3}
        supabase.table("tentativas_usuario").insert(data).execute()
        return 3
    return response.data[0]["tentativas_restantes"]


def decrementar_tentativa(usuario_id, enigma_id):
    response = supabase.table("tentativas_usuario").update({
        "tentativas_restantes": supabase.raw("GREATEST(tentativas_restantes - 1, 0)")  # Impede valores negativos
    }).eq("usuario_id", usuario_id).eq("enigma_id", enigma_id).execute()
    return response.status_code == 200


def enigma_concluido(usuario_id, enigma_id):
    response = supabase.table("enigmas_respondidos").select("*").eq("usuario_id", usuario_id).eq("enigma_id", enigma_id).execute()
    return len(response.data) > 0 and response.data[0]["concluido"] == True


def marcar_concluido(usuario_id, enigma_id):
    data = {"usuario_id": usuario_id, "enigma_id": enigma_id, "concluido": True}
    response = supabase.table("enigmas_respondidos").upsert([data]).execute()
    return response.status_code == 200
