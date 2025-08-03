import asyncio
import hashlib
from datetime import datetime
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from utils.binance_intent_parser import detectar_intencao_binance, carregar_tools_binance
from mcp_servers import MCP_BINANCE
from prompts_agents import agent_binance
from utils.memory_manager import PersistentMemoryManager

async def main():
    print("🚀 Agente Binance Trading com Memória Persistente")
    print("📊 Especialista em análise de mercado e automação de trading")
    print("=" * 60)
    
    # Inicializar gerenciador de memória
    memory_manager = PersistentMemoryManager()
    
    # Gerar IDs únicos
    user_id = hashlib.md5("binance_user".encode()).hexdigest()[:16]
    thread_id = f"binance_{user_id}"
    
    print(f"👤 User ID: {user_id}")
    print(f"🧵 Thread ID: {thread_id}")
    
    llm = init_chat_model("google_genai:gemini-2.0-flash")
    checkpointer = memory_manager.get_sqlite_saver("binance")
    
    config = {"configurable": {"thread_id": thread_id}}
    
    print("\n💡 Digite 'help' para ver comandos disponíveis")
    print("💡 Digite 'prefs' para configurar preferências de trading")
    print("💡 Digite 'metrics' para ver métricas de performance")
    print("-" * 50)

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
• Memória: "limpar contexto", "salvar preferência"
• Geral: qualquer pergunta sobre trading na Binance
            """)
            continue
        
        if entrada.lower() == 'prefs':
            print("\n⚙️ Configurar Preferências de Trading:")
            key = input("Chave (ex: risk_level, preferred_pairs): ")
            value = input("Valor: ")
            memory_manager.save_user_preference(user_id, key, value, "binance")
            print(f"✅ Preferência '{key}' salva com sucesso!")
            continue
        
        if entrada.lower() == 'metrics':
            metrics = memory_manager.get_performance_metrics("binance", user_id)
            print(f"\n📊 Métricas de Trading dos últimos 30 dias: {len(metrics)} registros")
            for metric in metrics[-5:]:  # Últimas 5
                print(f"  • {metric['type']}: {metric['value']} ({metric['timestamp']})")
            continue
            
        if entrada.lower() in ['exit', 'quit', 'sair']:
            print("👋 Encerrando agente Binance...")
            break
        
        # Detectar intenção
        intencao = detectar_intencao_binance(entrada)
        print(f"📍 Intenção detectada: {intencao}")
        
        # Recuperar contexto anterior
        contexto_anterior = memory_manager.get_conversation_context(thread_id, "binance", limit=5)
        user_preferences = memory_manager.get_user_preferences(user_id, "binance")
        
        # Construir contexto enriquecido
        contexto_enriquecido = ""
        if contexto_anterior:
            contexto_enriquecido += "\n\n[CONTEXTO TRADING ANTERIOR]:\n"
            for ctx in contexto_anterior:
                contexto_enriquecido += f"- {ctx['type']}: {str(ctx['content'])[:200]}...\n"
        
        if user_preferences:
            contexto_enriquecido += "\n[PREFERÊNCIAS DE TRADING]:\n"
            for key, value in user_preferences.items():
                contexto_enriquecido += f"- {key}: {value}\n"
        
        # Carregar ferramentas
        tools = await carregar_tools_binance(intencao, MCP_BINANCE)
        print(f"🔧 Tools carregadas: {len(tools)}")
        
        # Criar agente com contexto
        agente = create_react_agent(
            model=llm,
            tools=tools,
            prompt=agent_binance + contexto_enriquecido,
            checkpointer=checkpointer,
        )
        
        # Atualizar atividade da sessão
        memory_manager.update_session_activity(thread_id)
        
        mensagem = {"role": "user", "content": entrada}
        
        print("🤖 Processando...")
        start_time = datetime.now()
        
        response_content = ""
        async for step in agente.astream({"messages": [mensagem]}, config, stream_mode="values"):
            if "messages" in step and step["messages"]:
                last_message = step["messages"][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    content = last_message.content
                    if isinstance(content, list):
                        content = '\n\n'.join(str(item) for item in content if item)
                    response_content += str(content)
                    step["messages"][-1].pretty_print()
        
        # Calcular tempo de resposta
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Salvar contexto importante
        memory_manager.save_conversation_context(thread_id, {
            'type': intencao,
            'content': {
                'prompt': entrada,
                'response': response_content[:500],
                'timestamp': datetime.now().isoformat(),
                'tools_used': len(tools)
            },
            'importance': 3 if intencao in ['trading_automatico', 'gestao_risco'] else 2
        }, "binance")
        
        # Salvar métricas de performance
        memory_manager.save_performance_metric("binance", user_id, "response_time", response_time)
        memory_manager.save_performance_metric("binance", user_id, "response_length", len(response_content))
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())