import re

def detectar_intencao_bet365(mensagem: str) -> str:
    """
    Detecta a intenção específica para apostas na Bet365
    """
    if not mensagem:
        return "geral"

    mensagem = mensagem.lower()

    # Análise esportiva
    if any(palavra in mensagem for palavra in ["análise", "analise", "estatística", "estatistica", "time", "jogador", "equipe", "histórico", "historico", "forma", "desempenho"]):
        return "analise_esportiva"
    
    # Gestão de apostas
    if any(palavra in mensagem for palavra in ["aposta", "apostar", "bet", "stake", "bankroll", "gestão", "gestao", "estratégia", "estrategia"]):
        return "gestao_apostas"
    
    # Análise de odds
    if any(palavra in mensagem for palavra in ["odds", "cotação", "cotacao", "probabilidade", "value", "arbitragem", "comparar"]):
        return "analise_odds"
    
    # Esportes específicos
    if any(palavra in mensagem for palavra in ["futebol", "football", "soccer", "copa", "campeonato", "liga"]):
        return "futebol"
    elif any(palavra in mensagem for palavra in ["basquete", "basketball", "nba", "euroliga"]):
        return "basquete"
    elif any(palavra in mensagem for palavra in ["tênis", "tennis", "atp", "wta", "grand slam"]):
        return "tenis"
    elif any(palavra in mensagem for palavra in ["e-sports", "esports", "cs:go", "lol", "dota"]):
        return "esports"
    
    # Relatórios e tracking
    if any(palavra in mensagem for palavra in ["relatório", "relatorio", "roi", "lucro", "prejuízo", "prejuizo", "performance", "histórico", "historico"]):
        return "relatorios"
    
    # Configuração
    if any(palavra in mensagem for palavra in ["configurar", "setup", "conta", "login", "api", "conectar"]):
        return "configuracao"

    return "geral"


async def carregar_tools_bet365(intencao: str, mcp_config: dict):
    """
    Carrega as tools específicas baseadas na intenção detectada para Bet365
    """
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Mapeamento de intenções para configurações específicas
        config_mapping = {
            "analise_esportiva": ["passos_sequenciais", "buscas_relevantes", "analise_esportiva"],
            "gestao_apostas": ["passos_sequenciais", "analise_esportiva"],
            "analise_odds": ["buscas_relevantes", "analise_esportiva"],
            "futebol": ["passos_sequenciais", "buscas_relevantes"],
            "basquete": ["passos_sequenciais", "buscas_relevantes"],
            "tenis": ["passos_sequenciais", "buscas_relevantes"],
            "esports": ["passos_sequenciais", "buscas_relevantes"],
            "relatorios": ["analise_esportiva", "passos_sequenciais"],
            "configuracao": ["passos_sequenciais", "buscas_relevantes"],
            "geral": ["passos_sequenciais", "buscas_relevantes", "analise_esportiva"]
        }
        
        # Seleciona as configurações baseadas na intenção
        selected_configs = config_mapping.get(intencao, config_mapping["geral"])
        
        # Cria um sub-config apenas com as tools necessárias
        sub_config = {key: mcp_config[key] for key in selected_configs if key in mcp_config}
        
        mcp_client = MultiServerMCPClient(sub_config)
        tools = await mcp_client.get_tools()
        return tools
        
    except ImportError:
        print("⚠️  Módulo langchain_mcp_adapters não encontrado.")
        print("📦 Instale com: pip install langchain-mcp-adapters==0.1.9")
        print("🔄 Retornando lista vazia de tools...")
        return []