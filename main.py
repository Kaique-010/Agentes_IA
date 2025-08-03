import asyncio
import hashlib
from datetime import datetime
from pprint import pprint
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from prompts_agents import agent_integration_ml
from mcp_servers import MCP_SERVERS_CONFIG
from utils.memory_manager import PersistentMemoryManager

async def main():
    print("🚀 Agente Principal de Integração ML com Memória Persistente")
    print("=" * 60)
    
    # Inicializar gerenciador de memória
    memory_manager = PersistentMemoryManager()
    
    # Gerar IDs únicos
    user_id = hashlib.md5("main_user".encode()).hexdigest()[:16]
    thread_id = f"main_{user_id}"
    
    print(f"👤 User ID: {user_id}")
    print(f"🧵 Thread ID: {thread_id}")
    
    llm = init_chat_model("google_genai:gemini-2.0-flash")
    checkpointer = memory_manager.get_sqlite_saver("main")
    
    try:
        mcp_client = MultiServerMCPClient(MCP_SERVERS_CONFIG)
        tools = await mcp_client.get_tools()
        print(f"🔧 Tools carregadas: {len(tools)}")
    except Exception as e:
        print(f"⚠️ Erro ao carregar MCP tools: {e}")
        tools = []
    
    # Recuperar contexto anterior
    contexto_anterior = memory_manager.get_conversation_context(thread_id, "main", limit=5)
    user_preferences = memory_manager.get_user_preferences(user_id, "main")
    
    # Construir contexto enriquecido
    contexto_enriquecido = ""
    if contexto_anterior:
        contexto_enriquecido += "\n\n[CONTEXTO ANTERIOR]:\n"
        for ctx in contexto_anterior:
            contexto_enriquecido += f"- {ctx['type']}: {str(ctx['content'])[:200]}...\n"
    
    if user_preferences:
        contexto_enriquecido += "\n[PREFERÊNCIAS DO USUÁRIO]:\n"
        for key, value in user_preferences.items():
            contexto_enriquecido += f"- {key}: {value}\n"
    
    execucao_agente = create_react_agent(
        model=llm,
        tools=tools,
        prompt=agent_integration_ml + contexto_enriquecido,
        checkpointer=checkpointer
    )

    config = {'configurable': {'thread_id': thread_id}}
    
    print("\n💡 Digite 'help' para comandos disponíveis")
    print("💡 Digite 'prefs' para configurar preferências")
    print("💡 Digite 'metrics' para ver métricas")
    print("-" * 60)

    while True:
        user_input = input('🤖 Main> ')
        
        if user_input.lower() in ['exit', 'quit', 'sair']:
            print("👋 Encerrando agente principal...")
            break
        
        if user_input.lower() == 'help':
            print("""
📋 Comandos disponíveis:
• Integração: "integrar API X", "documentação da API Y"
• Análise: "analisar endpoint", "swagger da API"
• Código: "gerar serializer", "criar service"
• Memória: "limpar contexto", "salvar preferência"
• Métricas: "mostrar performance", "estatísticas"
• Geral: qualquer pergunta sobre integração de APIs
            """)
            continue
        
        if user_input.lower() == 'prefs':
            print("\n⚙️ Configurar Preferências:")
            key = input("Chave da preferência: ")
            value = input("Valor da preferência: ")
            memory_manager.save_user_preference(user_id, key, value, "main")
            print(f"✅ Preferência '{key}' salva com sucesso!")
            continue
        
        if user_input.lower() == 'metrics':
            metrics = memory_manager.get_performance_metrics("main", user_id)
            print(f"\n📊 Métricas dos últimos 30 dias: {len(metrics)} registros")
            for metric in metrics[-5:]:  # Últimas 5
                print(f"  • {metric['type']}: {metric['value']} ({metric['timestamp']})")
            continue
        
        # Atualizar atividade da sessão
        memory_manager.update_session_activity(thread_id)
        
        mensagem = {'role': 'user', 'content': user_input}
        
        print("🤖 Processando...")
        start_time = datetime.now()
        
        response_content = ""
        async for step in execucao_agente.astream({"messages": [mensagem]}, config, stream_mode='values'):
            if 'messages' in step and step['messages']:
                last_message = step['messages'][-1]
                if hasattr(last_message, 'type') and last_message.type == 'ai':
                    if hasattr(last_message, 'content') and last_message.content:
                        content = last_message.content
                        if isinstance(content, list):
                            content = '\n\n'.join(str(item) for item in content if item)
                        response_content += str(content)
                        step['messages'][-1].pretty_print()
        
        # Calcular tempo de resposta
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Salvar contexto importante
        memory_manager.save_conversation_context(thread_id, {
            'type': 'integration',
            'content': {
                'prompt': user_input,
                'response': response_content[:500],
                'timestamp': datetime.now().isoformat(),
                'tools_used': len(tools)
            },
            'importance': 2 if len(response_content) > 100 else 1
        }, "main")
        
        # Salvar métricas de performance
        memory_manager.save_performance_metric("main", user_id, "response_time", response_time)
        memory_manager.save_performance_metric("main", user_id, "response_length", len(response_content))
        
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(main())