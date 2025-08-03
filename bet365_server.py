from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
import hashlib
from datetime import datetime

from prompts_agents import agent_bet365
from mcp_servers import MCP_BET365
from utils.bet365_intent_parser import detectar_intencao_bet365, carregar_tools_bet365
from utils.schemas import FormPrompt
from utils.memory_manager import PersistentMemoryManager

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar gerenciador de memória
memory_manager = PersistentMemoryManager()
agent_cache = {}

def get_user_id(request: Request) -> str:
    """Gera ID único do usuário baseado no IP"""
    client_ip = request.client.host
    return hashlib.md5(f"bet365_{client_ip}".encode()).hexdigest()[:16]

def get_thread_id(user_id: str) -> str:
    """Gera thread ID para o usuário"""
    return f"bet365_{user_id}"

@app.get("/", response_class=HTMLResponse)
async def bet365_index(request: Request):
    return templates.TemplateResponse("bet365_index.html", {"request": request})

@app.post("/bet365-agent")
async def process_bet365_prompt(request: Request, mensagem: str = Form(...)):
    try:
        if not mensagem or not mensagem.strip():
            return JSONResponse({"erro": "Mensagem não fornecida"}, status_code=400)
        
        prompt = mensagem.strip()
        user_id = get_user_id(request)
        thread_id = get_thread_id(user_id)
        
        print(f"⚽ Bet365 - User ID: {user_id}")
        print(f"🧵 Thread ID: {thread_id}")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Detectar intenção
        intencao = detectar_intencao_bet365(prompt)
        print(f"🎯 Intenção detectada: {intencao}")
        
        # Recuperar contexto anterior
        contexto_anterior = memory_manager.get_conversation_context(thread_id, "bet365", limit=5)
        user_preferences = memory_manager.get_user_preferences(user_id, "bet365")
        
        # Construir contexto enriquecido
        contexto_enriquecido = ""
        if contexto_anterior:
            contexto_enriquecido += "\n\n[CONTEXTO APOSTAS ANTERIOR]:\n"
            for ctx in contexto_anterior:
                contexto_enriquecido += f"- {ctx['type']}: {str(ctx['content'])[:200]}...\n"
        
        if user_preferences:
            contexto_enriquecido += "\n[PREFERÊNCIAS DE APOSTAS]:\n"
            for key, value in user_preferences.items():
                contexto_enriquecido += f"- {key}: {value}\n"
        
        # Carregar ferramentas
        tools = await carregar_tools_bet365(intencao, MCP_BET365)
        print(f"🔧 Tools carregadas: {len(tools)}")
        
        # Criar ou reutilizar agente
        if thread_id not in agent_cache:
            llm = init_chat_model("google_genai:gemini-2.0-flash")
            checkpointer = memory_manager.get_sqlite_saver("bet365")
            
            agente = create_react_agent(
                model=llm,
                tools=tools,
                prompt=agent_bet365 + contexto_enriquecido,
                checkpointer=checkpointer,
            )
            agent_cache[thread_id] = agente
            print(f"🤖 Novo agente Bet365 criado para {thread_id}")
        else:
            agente = agent_cache[thread_id]
            print(f"♻️ Reutilizando agente Bet365 para {thread_id}")
        
        # Atualizar atividade da sessão
        memory_manager.update_session_activity(thread_id)
        
        config = {"configurable": {"thread_id": thread_id}}
        mensagem_usuario = {"role": "user", "content": prompt}
        
        resposta = ""
        print("🤖 Processando com Bet365 Agent...")
        
        async for step in agente.astream({"messages": [mensagem_usuario]}, config, stream_mode="values"):
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
            resposta_final = "Desculpe, não consegui processar sua solicitação de apostas. Tente reformular."
        
        # Salvar contexto importante
        memory_manager.save_conversation_context(thread_id, {
            'type': intencao,
            'content': {
                'prompt': prompt,
                'response': resposta_final[:500],
                'timestamp': datetime.now().isoformat(),
                'tools_used': len(tools)
            },
            'importance': 3 if intencao in ['gestao_apostas', 'analise_odds'] else 2
        }, "bet365")
        
        # Salvar métrica de performance
        memory_manager.save_performance_metric("bet365", user_id, "response_length", len(resposta_final))
        
        print(f"✅ Resposta Bet365 gerada: {len(resposta_final)} caracteres")
        return JSONResponse({"resposta": resposta_final, "intencao": intencao})
        
    except Exception as e:
        print(f"❌ Erro no Bet365 Agent: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"erro": f"Erro interno: {str(e)}"}, status_code=500)

@app.post("/clear_bet365_memory")
async def clear_bet365_memory(request: Request):
    """Limpa a memória do usuário atual para Bet365"""
    try:
        user_id = get_user_id(request)
        thread_id = get_thread_id(user_id)
        
        if thread_id in agent_cache:
            del agent_cache[thread_id]
        
        return JSONResponse({"message": "Memória Bet365 limpa com sucesso"})
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)

@app.post("/save_bet365_preference")
async def save_bet365_preference(request: Request, key: str = Form(...), value: str = Form(...)):
    """Salva preferência do usuário para Bet365"""
    try:
        user_id = get_user_id(request)
        memory_manager.save_user_preference(user_id, key, value, "bet365")
        return JSONResponse({"message": "Preferência Bet365 salva com sucesso"})
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)

@app.get("/bet365_metrics")
async def get_bet365_metrics(request: Request):
    """Recupera métricas de performance do Bet365"""
    try:
        user_id = get_user_id(request)
        metrics = memory_manager.get_performance_metrics("bet365", user_id)
        return JSONResponse({"metrics": metrics})
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "bet365-agent", "memory": "enabled"}

if __name__ == "__main__":
    import uvicorn
    print("⚽ Iniciando Bet365 Agent com Memória Persistente...")
    print("🌐 Servidor disponível em: http://localhost:8003")
    uvicorn.run(app, host="127.0.0.1", port=8003, reload=True)