import os
from dotenv import load_dotenv

load_dotenv()

SMITHERY_API_KEY = os.getenv("SMITHERY_API_KEY")
if not SMITHERY_API_KEY:
    raise ValueError("SMITHERY_API_KEY não definida no ambiente.")

MCP_SERVERS_CONFIG = {
    'passos_sequenciais': {
        'url': f'https://server.smithery.ai/@xinzhongyouhai/mcp-sequentialthinking-tools/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
        'transport': 'streamable_http',
    },
    'buscas_relevantes': {
        'url': f'https://server.smithery.ai/@nickclyde/duckduckgo-mcp-server/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
        'transport': 'streamable_http',
    },
    'auxilio_apis': {
        'url': f'https://server.smithery.ai/@upstash/context7-mcp/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
        'transport': 'streamable_http',
    },
}
MCP_DEV_CONFIG = {
    "backend": {
        "django_boilerplate": {
            "url": f"https://server.smithery.ai/@smithery/toolbox/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu",
            "transport": "streamable_http",
        },
        "codigo_ajustado": {
           'url': f'https://server.smithery.ai/@upstash/context7-mcp/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
           'transport': 'streamable_http',
        },
    },
    "frontend": {
        "react_native_scaffold": {
            "url": f"https://server.smithery.ai/@seu-usuario/react-native-scaffold/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu",
            "transport": "streamable_http",
        },
        "gerador_snippet": {
            "url": f"https://server.smithery.ai/@Yaxin9Luo/openai_agent_library_mcp/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu",
            "transport": "streamable_http",
        },
    },
    "refatoracao": {
        "codigo_ajustado": {
           'url': f'https://server.smithery.ai/@upstash/context7-mcp/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
           'transport': 'streamable_http',
        },
        "avaliador_codigo": {
            'url': f'https://server.smithery.ai/@upstash/context7-mcp/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
            'transport': 'streamable_http',  
        },
    },
    "explicacao": {
        "explicador_codigo": {
           'url': f'https://server.smithery.ai/@upstash/context7-mcp/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
           'transport': 'streamable_http',
        }
    },
    "debug": {
        "busca_stackoverflow": {
            "url": f"https://server.smithery.ai/@nickclyde/duckduckgo-mcp-server/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu",
            "transport": "streamable_http",
        }
    },
    "snippet": {

        "busca_stackoverflow": {
            "url": f"https://server.smithery.ai/@nickclyde/duckduckgo-mcp-server/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu",
            "transport": "streamable_http",
        }
    },
    "geral": {
        "codigo_ajustado": {
            'url': f'https://server.smithery.ai/@xinzhongyouhai/mcp-sequentialthinking-tools/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
            'transport': 'streamable_http',
        },
        "explicador_codigo": {
           'url': f'https://server.smithery.ai/@upstash/context7-mcp/mcp?api_key={SMITHERY_API_KEY}&profile=liable-rhinoceros-zBrJHu',
           'transport': 'streamable_http',
        },
    },
}
