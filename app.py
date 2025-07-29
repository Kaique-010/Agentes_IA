import asyncio
import uuid
import logging
import os

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from prompts_agents import agent_integration_ml
from mcp_servers import MCP_SERVERS_CONFIG

# Carrega .env
load_dotenv()

# Configura FastAPI
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="sua_chave_secreta_aqui_mude_para_producao")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Armazenar agentes por sessão
agents = {}

# Dados do request
class ChatRequest(BaseModel):
    message: str

# Criação do agente
async def create_agent_with_fallback():
    llm = init_chat_model("google_genai:gemini-2.5-flash")
    memoria = MemorySaver()
    tools = []
    successful_servers = []

    for server_name, server_config in MCP_SERVERS_CONFIG.items():
        try:
            logger.info(f"Tentando conectar ao servidor {server_name}...")
            single_server_config = {server_name: server_config}
            mcp_client = MultiServerMCPClient(single_server_config)
            server_tools = await mcp_client.get_tools()
            tools.extend(server_tools)
            successful_servers.append(server_name)
            logger.info(f"Servidor {server_name} conectado com sucesso")
        except Exception as e:
            logger.warning(f"Falha ao conectar ao servidor {server_name}: {str(e)}")
            continue

    if not tools:
        logger.warning("Nenhum servidor MCP conectado, criando agente sem ferramentas externas")

    execucao_agente = create_react_agent(
        model=llm,
        tools=tools,
        prompt=agent_integration_ml,
        checkpointer=memoria
    )

    return execucao_agente

# Execução assíncrona
async def run_agent_async(agent, message, config):
    try:
        responses = []
        async for chunk in agent.astream({"messages": [message]}, config):
            if 'messages' in chunk:
                for msg in chunk['messages']:
                    if hasattr(msg, 'content') and msg.content:
                        responses.append({
                            'type': getattr(msg, 'type', 'ai'),
                            'content': msg.content
                        })

        return {'success': True, 'responses': responses}

    except Exception as e:
        logger.error(f"Erro na execução do agente: {str(e)}")
        return {'success': False, 'error': str(e)}

# Endpoint principal
@app.post("/chat")
async def chat_endpoint(chat: ChatRequest, request: Request):
    session_id = request.session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['session_id'] = session_id

    message_text = chat.message.strip()
    if not message_text:
        return JSONResponse(status_code=400, content={'error': 'Mensagem vazia'})

    logger.info(f"[{session_id}] Pergunta: {message_text[:60]}")

    # Criar agente se necessário
    if session_id not in agents:
        logger.info(f"Criando agente novo para {session_id}")
        try:
            agents[session_id] = await create_agent_with_fallback()
        except Exception as e:
            return JSONResponse(status_code=500, content={'error': f'Erro ao criar agente: {str(e)}'})

    agent = agents[session_id]
    config = {'configurable': {'thread_id': session_id}}
    mensagem = {'role': 'user', 'content': message_text}

    result = await run_agent_async(agent, mensagem, config)

    if result['success']:
        return {'responses': result['responses'], 'user_message': message_text}
    else:
        return JSONResponse(status_code=500, content={'error': result['error']})

# Endpoint pra limpar a sessão
@app.post("/clear")
async def clear_session(request: Request):
    session_id = request.session.get('session_id')
    if session_id and session_id in agents:
        del agents[session_id]
        logger.info(f"Sessão {session_id} limpa")
    request.session['session_id'] = str(uuid.uuid4())
    return {'success': True}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id

    return templates.TemplateResponse("index.html", {"request": request})
