import re
from langchain_mcp_adapters.client import MultiServerMCPClient

def detectar_intencao(mensagem: str) -> str:
    if not mensagem:
        return "geral"

    mensagem = mensagem.lower()

    if "serializer" in mensagem or "model" in mensagem or "view" in mensagem or "drf" in mensagem or "django" in mensagem:
        return "backend"
    if "react native" in mensagem or "component" in mensagem or "hook" in mensagem or "context" in mensagem:
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
    sub_config = mcp_config.get(intencao, mcp_config["geral"])
    mcp_client = MultiServerMCPClient(sub_config)
    tools = await mcp_client.get_tools()
    return tools