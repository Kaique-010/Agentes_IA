from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from prompts_agents import agent_bet365
from mcp_servers import MCP_BET365
from utils.bet365_intent_parser import detectar_intencao_bet365, carregar_tools_bet365
from utils.schemas import FormPrompt

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def bet365_index(request: Request):
    return templates.TemplateResponse("bet365_index.html", {"request": request})


@app.post("/bet365-agent")
async def process_bet365_prompt(mensagem: str = Form(...)):
    try:
        prompt = FormPrompt(mensagem=mensagem.strip())
    except ValidationError as e:
        return JSONResponse(content={"resposta": f"❌ Erro: {e.errors()[0]['msg']}"})

    intencao = detectar_intencao_bet365(prompt.mensagem)
    tools = await carregar_tools_bet365(intencao, MCP_BET365)
    llm = init_chat_model("google_genai:gemini-2.0-flash")
    memoria = MemorySaver()

    agente = create_react_agent(
        model=llm,
        tools=tools,
        prompt=agent_bet365,
        checkpointer=memoria,
    )

    config = {"configurable": {"thread_id": "bet365_agent"}}
    mensagem_usuario = {"role": "user", "content": prompt.mensagem}

    resposta = ""
    async for step in agente.astream({"messages": [mensagem_usuario]}, config, stream_mode="values"):
        resposta += step["messages"][-1].content

    return JSONResponse(content={"resposta": resposta, "intencao": intencao})


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "bet365-agent"}