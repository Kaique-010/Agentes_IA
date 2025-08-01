import asyncio
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from utils.binance_intent_parser import detectar_intencao_binance, carregar_tools_binance
from mcp_servers import MCP_BINANCE
from prompts_agents import agent_binance


async def main():
    print("🚀 Agente Binance Trading Ativo")
    print("📊 Especialista em análise de mercado e automação de trading")
    print("💡 Digite 'help' para ver comandos disponíveis")
    print("-" * 50)

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    memoria = MemorySaver()

    config = {"configurable": {"thread_id": "binance_agent_001"}}

    while True:
        entrada = input("💰 Binance> ")
        
        if entrada.lower() == 'help':
            print("""
📋 Comandos disponíveis:
• Análise: "analise o BTC/USDT", "indicadores técnicos do ETH"
• Trading: "criar estratégia de compra", "executar ordem de venda"
• Risco: "calcular stop loss", "gerenciar posição"
• Monitoramento: "relatório de performance", "histórico de trades"
• Configuração: "configurar API", "setup de autenticação"
• Geral: qualquer pergunta sobre trading na Binance
            """)
            continue
            
        if entrada.lower() in ['exit', 'quit', 'sair']:
            print("👋 Encerrando agente Binance...")
            break

        intencao = detectar_intencao_binance(entrada)
        print(f"📍 Intenção detectada: {intencao}")

        tools = await carregar_tools_binance(intencao, MCP_BINANCE)
        print(f"🔧 Tools carregadas: {len(tools)}")

        agente = create_react_agent(
            model=llm,
            tools=tools,
            prompt=agent_binance,
            checkpointer=memoria,
        )

        mensagem = {"role": "user", "content": entrada}
        
        print("🤖 Processando...")
        async for step in agente.astream({"messages": [mensagem]}, config, stream_mode="values"):
            step["messages"][-1].pretty_print()
        
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())