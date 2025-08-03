"""Agente de programação para django e react native"""

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from utils.intent_parser import detectar_intencao, carregar_tools_por_intencao, esta_em_fallback
from utils.memory_manager import MemoryManager
from mcp_servers import MCP_DEV_CONFIG
import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Inicializar gerenciador de memória
memory_manager = MemoryManager()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Cache de agentes por thread
agent_cache = {}

def get_user_id(request: Request) -> str:
    """Gera ID único do usuário baseado no IP"""
    client_ip = request.client.host
    return hashlib.md5(client_ip.encode()).hexdigest()[:8]

def get_thread_id(user_id: str, session_type: str = "dev") -> str:
    """Gera thread_id único para o usuário e tipo de sessão"""
    return f"{session_type}_{user_id}"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("devindex.html", {"request": request})

@app.post("/agent")
async def process_prompt(request: Request, mensagem: str = Form(...)):
    try:
        if not mensagem or not mensagem.strip():
            return JSONResponse({"erro": "Mensagem não fornecida"}, status_code=400)
        
        prompt = mensagem.strip()
        user_id = get_user_id(request)
        thread_id = get_thread_id(user_id)
        
        print(f"👤 User ID: {user_id}")
        print(f"🧵 Thread ID: {thread_id}")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Detectar intenção
        intencao = detectar_intencao(prompt)
        print(f"🎯 Intenção detectada: {intencao}")
        
        # Recuperar contexto anterior
        contexto_anterior = memory_manager.get_conversation_context(thread_id, limit=5)
        user_preferences = memory_manager.get_user_preferences(user_id)
        
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
        
        # Carregar ferramentas
        tools = await carregar_tools_por_intencao(intencao, MCP_DEV_CONFIG)
        
        # Configurar modelo
        modelo = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )
        
        # Usar agente do cache ou criar novo
        if thread_id not in agent_cache:
            checkpointer = memory_manager.get_sqlite_saver()
            if tools:
                agent_cache[thread_id] = create_react_agent(modelo, tools, checkpointer=checkpointer)
            else:
                agent_cache[thread_id] = create_react_agent(modelo, [], checkpointer=checkpointer)
            print(f"🆕 Novo agente criado para thread {thread_id}")
        else:
            print(f"♻️ Reutilizando agente existente para thread {thread_id}")
        
        agente = agent_cache[thread_id]
        
        # Processar resposta
        resposta = ""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Prompt completo com contexto
        prompt_completo = f"{contexto_enriquecido}\n\n[PERGUNTA ATUAL]: {prompt}"
        
        if esta_em_fallback():
            prompt_completo += "\n\n[MODO FALLBACK ATIVO: Funcionando sem ferramentas MCP externas]"
        
        print(f"🚀 Processando com contexto...")
        
        async for step in agente.astream({"messages": [("user", prompt_completo)]}, config, stream_mode='values'):
            if "messages" in step and step["messages"]:
                ultima_mensagem = step["messages"][-1]
                
                if hasattr(ultima_mensagem, 'type') and ultima_mensagem.type == 'ai':
                    if hasattr(ultima_mensagem, 'content') and ultima_mensagem.content:
                        if isinstance(ultima_mensagem.content, list):
                            conteudo = '\n\n'.join(str(item) for item in ultima_mensagem.content if item)
                        else:
                            conteudo = str(ultima_mensagem.content)
                        
                        if conteudo.strip():
                            resposta += conteudo + "\n"
        
        resposta_final = resposta.strip()
        
        if not resposta_final:
            resposta_final = "Desculpe, não consegui gerar uma resposta. Tente reformular a pergunta."
        
        # Salvar contexto importante
        memory_manager.save_conversation_context(thread_id, {
            'type': intencao,
            'content': {
                'prompt': prompt,
                'response': resposta_final[:500],  # Primeiros 500 chars
                'timestamp': datetime.now().isoformat()
            },
            'importance': 2 if len(resposta_final) > 100 else 1
        })
        
        print(f"✅ Resposta gerada e contexto salvo: {len(resposta_final)} caracteres")
        return JSONResponse({"resposta": resposta_final})
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"erro": f"Erro interno: {str(e)}"}, status_code=500)

@app.post("/clear_memory")
async def clear_memory(request: Request):
    """Limpa a memória do usuário atual"""
    try:
        user_id = get_user_id(request)
        thread_id = get_thread_id(user_id)
        
        # Remove do cache
        if thread_id in agent_cache:
            del agent_cache[thread_id]
        
        return JSONResponse({"message": "Memória limpa com sucesso"})
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)

@app.post("/save_preference")
async def save_preference(request: Request, key: str = Form(...), value: str = Form(...)):
    """Salva preferência do usuário"""
    try:
        user_id = get_user_id(request)
        memory_manager.save_user_preference(user_id, key, value)
        return JSONResponse({"message": "Preferência salva com sucesso"})
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)

async def get_or_create_agent(user_id: str, agent_type: str = "default"):
    thread_id = f"{agent_type}_{user_id}"
    
    if thread_id in agents:
        return agents[thread_id], thread_id
    
    print(f"🆕 Novo agente criado para thread {thread_id}")
    
    # Conectar ao servidor MCP apropriado
    mcp_client = await connect_to_mcp_server(agent_type)
    
    # Obter ferramentas do servidor MCP
    tools = await get_mcp_tools(mcp_client)
    
    # Criar checkpointer (não assíncrono)
    checkpointer = memory_manager.get_sqlite_saver(agent_type)
    
    # Criar agente
    agente = create_react_agent(model, tools, checkpointer=checkpointer)
    agents[thread_id] = agente
    
    return agente, thread_id

@app.get("/memory_status")
async def memory_status(request: Request):
    """Retorna o status da memória"""
    user_id = get_user_id(request)
    thread_id = get_thread_id(user_id)
    
    # Obter estatísticas básicas
    context_count = len(memory_manager.get_conversation_context(thread_id, "default"))
    
    return JSONResponse({
        "status": "active",
        "thread_id": thread_id,
        "context_items": context_count,
        "last_updated": datetime.now().isoformat()
    })

@app.get("/get_context")
async def get_context(request: Request):
    """Retorna o contexto da conversa"""
    user_id = get_user_id(request)
    thread_id = get_thread_id(user_id)
    
    context = memory_manager.get_conversation_context(thread_id, "default")
    
    return JSONResponse({
        "context": context,
        "thread_id": thread_id
    })

@app.get("/metrics")
async def metrics(request: Request, agent_type: str = "default"):
    """Retorna métricas de performance"""
    user_id = get_user_id(request)
    
    metrics = memory_manager.get_performance_metrics(agent_type, user_id)
    
    return JSONResponse({
        "metrics": metrics,
        "user_id": user_id,
        "agent_type": agent_type
    })

if __name__ == "__main__":
    print("🚀 Iniciando Agente Programador com Memória Persistente...")
    print("🌐 Servidor disponível em: http://localhost:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
