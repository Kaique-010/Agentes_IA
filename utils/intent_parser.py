import re
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

# Cache global para clientes MCP com controle de sessão
_mcp_clients_cache = {}
_session_locks = {}
_fallback_mode = False

def detectar_intencao(mensagem: str) -> str:
    if not mensagem:
        return "geral"

    mensagem = mensagem.lower()

    if "serializer" in mensagem or "model" in mensagem or "view" in mensagem or "drf" in mensagem or "django" in mensagem:
        return "backend"
    if "react native" in mensagem or "component" in mensagem or "hook" in mensagem or "context" or "tela" in mensagem:
        return "frontend"
    if "refatore" in mensagem or "melhore" in mensagem or "otimize" in mensagem:
        return "refatoracao"
    if "explique" in mensagem or "o que faz" in mensagem or "entenda esse código" in mensagem:
        return "explicacao"
    if "erro" in mensagem or "stacktrace" in mensagem or "exception" in mensagem:
        return "debug"
    if "snippet" in mensagem or "exemplo" in mensagem or "como faço" in mensagem:
        return "snippet"

    return "geral"


async def carregar_tools_por_intencao(intencao: str, mcp_config: dict):
    global _fallback_mode
    
    # Se já estamos em modo fallback, retornar lista vazia
    if _fallback_mode:
        print(f"🔄 Modo fallback ativo - agente funcionará sem ferramentas MCP")
        return []
    
    # Tentar carregar ferramentas MCP com timeout reduzido
    try:
        cache_key = f"{intencao}_{hash(str(mcp_config.get(intencao, mcp_config['geral'])))}"
        
        # Criar lock se não existir
        if cache_key not in _session_locks:
            _session_locks[cache_key] = asyncio.Lock()
        
        async with _session_locks[cache_key]:
            # Verificar cache primeiro
            if cache_key in _mcp_clients_cache:
                try:
                    tools = await asyncio.wait_for(_mcp_clients_cache[cache_key].get_tools(), timeout=5.0)
                    print(f"✅ Ferramentas MCP carregadas do cache para {intencao}")
                    return tools
                except Exception:
                    del _mcp_clients_cache[cache_key]
            
            # Tentar criar nova conexão com timeout muito baixo
            sub_config = mcp_config.get(intencao, mcp_config["geral"])
            mcp_client = MultiServerMCPClient(sub_config)
            
            # Timeout agressivo de apenas 8 segundos
            tools = await asyncio.wait_for(mcp_client.get_tools(), timeout=8.0)
            _mcp_clients_cache[cache_key] = mcp_client
            print(f"✅ Nova conexão MCP estabelecida para {intencao}")
            return tools
            
    except Exception as e:
        print(f"⚠️ Falha nas ferramentas MCP: {e}")
        print(f"🔄 Ativando modo fallback - agente continuará sem ferramentas MCP")
        _fallback_mode = True
        return []


# Função para tentar reativar MCP
async def tentar_reativar_mcp():
    global _fallback_mode
    _fallback_mode = False
    limpar_cache_mcp()
    print("🔄 Tentando reativar conexões MCP...")


# Função para limpar cache
def limpar_cache_mcp():
    global _mcp_clients_cache, _session_locks
    _mcp_clients_cache.clear()
    _session_locks.clear()
    print("🧹 Cache MCP limpo")


# Função para verificar se está em modo fallback
def esta_em_fallback():
    return _fallback_mode


# Função para verificar status das conexões
async def verificar_status_conexoes():
    status = {}
    for cache_key, client in _mcp_clients_cache.items():
        try:
            await asyncio.wait_for(client.get_tools(), timeout=5.0)
            status[cache_key] = "OK"
        except Exception as e:
            status[cache_key] = f"ERRO: {e}"
    return status