from utils.intent_parser import detectar_intencao
from utils.intent_parser import carregar_tools_por_intencao  
from mcp_dev import MCP_DEV_CONFIG
from prompts_agents import agent_programador


async def main():
    print("🚀 Agente Programador Ativo")

    llm = init_chat_model("google_genai:gemini-2.5-flash-lite")
    memoria = MemorySaver()

    config = {"configurable": {"thread_id": "agent_dev_001"}}

    while True:
        entrada = input("💡 Dev> ")
        intencao = detectar_intencao(entrada)
        print(f"📍 Detecção: {intencao}")

        tools = await carregar_tools_por_intencao(intencao, MCP_DEV_CONFIG)

        agente = create_react_agent(
            model=llm,
            tools=tools,
            prompt=agent_programador,
            checkpointer=memoria,
        )

        mensagem = {"role": "user", "content": entrada}
        async for step in agente.astream({"messages": [mensagem]}, config, stream_mode="values"):
            step["messages"][-1].pretty_print()

if __name__ == "__main__":
    asyncio.run(main())
