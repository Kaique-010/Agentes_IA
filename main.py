import asyncio
from pprint import pprint
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from prompts_agents import agent_integration_ml
from mcp_servers import MCP_SERVERS_CONFIG

async def main():

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    memoria = MemorySaver()
    mcp_client = MultiServerMCPClient(MCP_SERVERS_CONFIG)
    tools = await mcp_client.get_tools()

    execucao_agente = create_react_agent(
        model=llm,
        tools=tools,
        prompt=agent_integration_ml,
        checkpointer=memoria
    )

    config = {'configurable': {'thread_id': '1'}}

    while True:
        user_input = input('Digite: ')
        mensagem = {'role': 'user', 'content': user_input}
        async for step in execucao_agente.astream({"messages": [mensagem]}, config, stream_mode='values'):
            step['messages'][-1].pretty_print()

asyncio.run(main())