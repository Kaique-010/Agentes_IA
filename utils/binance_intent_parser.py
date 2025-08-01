import re
from langchain_mcp_adapters.client import MultiServerMCPClient

def detectar_intencao_binance(mensagem: str) -> str:
    """
    Detecta a intenção específica para operações na Binance
    """
    if not mensagem:
        return "geral"

    mensagem = mensagem.lower()

    # Análise de mercado
    if any(palavra in mensagem for palavra in ["análise", "analise", "preço", "precos", "gráfico", "grafico", "tendência", "tendencia", "indicador", "rsi", "macd", "bollinger"]):
        return "analise_mercado"
    
    # Trading automático
    if any(palavra in mensagem for palavra in ["comprar", "vender", "ordem", "trade", "trading", "bot", "automatico", "automático", "estratégia", "estrategia"]):
        return "trading_automatico"
    
    # Gestão de risco
    if any(palavra in mensagem for palavra in ["risco", "stop", "loss", "profit", "posição", "posicao", "portfolio", "diversificação", "diversificacao"]):
        return "gestao_risco"
    
    # Monitoramento e relatórios
    if any(palavra in mensagem for palavra in ["relatório", "relatorio", "performance", "lucro", "prejuízo", "prejuizo", "histórico", "historico", "monitorar"]):
        return "monitoramento"
    
    # Configuração e setup
    if any(palavra in mensagem for palavra in ["configurar", "setup", "api", "chave", "conectar", "autenticação", "autenticacao"]):
        return "configuracao"

    return "geral"


async def carregar_tools_binance(intencao: str, mcp_config: dict):
    """
    Carrega as tools específicas baseadas na intenção detectada para Binance
    """
    # Mapeamento de intenções para configurações específicas
    config_mapping = {
        "analise_mercado": ["passos_sequenciais", "buscas_relevantes"],
        "trading_automatico": ["passos_sequenciais", "automacao"],
        "gestao_risco": ["passos_sequenciais", "automacao"],
        "monitoramento": ["buscas_relevantes", "automacao"],
        "configuracao": ["passos_sequenciais", "buscas_relevantes"],
        "geral": ["passos_sequenciais", "buscas_relevantes", "automacao"]
    }
    
    # Seleciona as configurações baseadas na intenção
    selected_configs = config_mapping.get(intencao, config_mapping["geral"])
    
    # Cria um sub-config apenas com as tools necessárias
    sub_config = {key: mcp_config[key] for key in selected_configs if key in mcp_config}
    
    mcp_client = MultiServerMCPClient(sub_config)
    tools = await mcp_client.get_tools()
    return tools