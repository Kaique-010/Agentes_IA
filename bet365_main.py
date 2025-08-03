import asyncio
import sys

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    missing_modules = []
    
    try:
        from langchain.chat_models import init_chat_model
    except ImportError:
        missing_modules.append("langchain")
    
    try:
        from langgraph.checkpoint.memory import MemorySaver
        from langgraph.prebuilt import create_react_agent
    except ImportError:
        missing_modules.append("langgraph")
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        missing_modules.append("langchain-mcp-adapters")
    
    if missing_modules:
        print("❌ Módulos faltando:")
        for module in missing_modules:
            print(f"   • {module}")
        print("\n📦 Instale com:")
        print("   pip install -r requirements.txt")
        print("\n🔄 Ou instale individualmente:")
        for module in missing_modules:
            print(f"   pip install {module}")
        return False
    
    return True

async def main():
    print("🎯 Agente Bet365 Sports Betting")
    print("=" * 40)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Não é possível continuar sem as dependências.")
        return
    
    # Imports após verificação
    from langchain.chat_models import init_chat_model
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.prebuilt import create_react_agent
    from utils.bet365_intent_parser import detectar_intencao_bet365, carregar_tools_bet365
    from mcp_servers import MCP_BET365
    from prompts_agents import agent_bet365

    print("✅ Dependências verificadas")
    print("⚽ Especialista em análise esportiva e apostas responsáveis")
    print("💡 Digite 'help' para ver comandos disponíveis")
    print("-" * 50)

    try:
        llm = init_chat_model("google_genai:gemini-2.0-flash")
        memoria = MemorySaver()
        print("✅ LLM inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar LLM: {e}")
        print("🔧 Verifique se a variável GOOGLE_API_KEY está configurada")
        return

    config = {"configurable": {"thread_id": "bet365_agent_001"}}

    # Inicializar gerenciador de memória
    from utils.memory_manager import PersistentMemoryManager
    memory_manager = PersistentMemoryManager()
    
    # Gerar IDs únicos
    import hashlib
    user_id = hashlib.md5("bet365_user".encode()).hexdigest()[:16]
    thread_id = f"bet365_{user_id}"
    
    print(f"👤 User ID: {user_id}")
    print(f"🧵 Thread ID: {thread_id}")
    
    checkpointer = memory_manager.get_sqlite_saver("bet365")
    
    while True:
        try:
            entrada = input("🎯 Bet365> ")
            
            if entrada.lower() == 'help':
                print("""
📋 Comandos disponíveis:
• Análise: "analise Real Madrid vs Barcelona", "estatísticas do Flamengo"
• Apostas: "estratégia para Champions League", "gestão de bankroll"
• Odds: "comparar odds Liverpool", "value bet Premier League"
• Esportes: "análise NBA Lakers", "previsão ATP Roland Garros"
• Relatórios: "ROI mensal", "performance por esporte"
• Configuração: "setup conta bet365", "configurar limites"
• Geral: qualquer pergunta sobre apostas esportivas
• help: mostra esta ajuda
• exit/quit/sair: encerra o programa

⚠️ LEMBRE-SE: Aposte com responsabilidade!
                """)
                continue
                
            if entrada.lower() in ['exit', 'quit', 'sair']:
                print("👋 Encerrando agente Bet365...")
                print("🎯 Lembre-se sempre de apostar com responsabilidade!")
                break

            intencao = detectar_intencao_bet365(entrada)
            print(f"📍 Intenção detectada: {intencao}")

            tools = await carregar_tools_bet365(intencao, MCP_BET365)
            print(f"🔧 Tools carregadas: {len(tools)}")

            agente = create_react_agent(
                model=llm,
                tools=tools,
                prompt=agent_bet365,
                checkpointer=memoria,
            )

            mensagem = {"role": "user", "content": entrada}
            
            print("🤖 Analisando...")
            async for step in agente.astream({"messages": [mensagem]}, config, stream_mode="values"):
                step["messages"][-1].pretty_print()
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Encerrando agente Bet365...")
            print("🎯 Lembre-se sempre de apostar com responsabilidade!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            print("🔄 Continuando...")
            continue


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Programa encerrado pelo usuário")
        print("🎯 Aposte sempre com responsabilidade!")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")