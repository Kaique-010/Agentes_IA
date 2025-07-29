from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from prompts_agents import agent_programador
from mcp_servers import MCP_DEV_CONFIG
from utils.intent_parser import detectar_intencao, carregar_tools_por_intencao
from utils.schemas import FormPrompt

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dev_index(request: Request):
    return templates.TemplateResponse("devindex.html", {"request": request})


@app.post("/agent")
async def process_prompt(mensagem: str = Form(...)):
    try:
        prompt = FormPrompt(mensagem=mensagem.strip())
    except ValidationError as e:
        return JSONResponse(content={"resposta": f"❌ Erro: {e.errors()[0]['msg']}"})

    intencao = detectar_intencao(prompt.mensagem)
    tools = await carregar_tools_por_intencao(intencao, MCP_DEV_CONFIG)
    llm = init_chat_model("google_genai:gemini-2.0-flash")
    memoria = MemorySaver()

    agente = create_react_agent(
        model=llm,
        tools=tools,
        prompt=agent_programador,
        checkpointer=memoria,
    )

    config = {"configurable": {"thread_id": "web_index"}}
    mensagem_usuario = {"role": "user", "content": prompt.mensagem}

    resposta = ""
    async for step in agente.astream({"messages": [mensagem_usuario]}, config, stream_mode="values"):
        resposta += step["messages"][-1].content

    return JSONResponse(content={"resposta": resposta})
