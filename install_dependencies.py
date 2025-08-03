"""
Script para instalar dependências dos agentes IA
"""
import subprocess
import sys
import os

def install_package(package):
    """Instala um pacote usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package):
    """Verifica se um pacote está instalado"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    print("🚀 Instalador de Dependências - Sistema de Agentes IA")
    print("=" * 55)
    
    # Lista das dependências principais
    dependencies = [
        "fastapi",
        "uvicorn[standard]",
        "langchain",
        "langchain-core",
        "langchain-google-genai",
        "langchain-mcp-adapters",
        "langgraph",
        "langgraph-checkpoint",
        "langgraph-prebuilt",
        "mcp",
        "fastmcp",
        "python-dotenv",
        "flask",
        "requests",
        "httpx",
        "pydantic",
        "google-generativeai",
        "openai",
        "numpy",
        "pandas",
        "rich",
        "tqdm",
        "jinja2",
        "werkzeug",
        "click",
        "colorama",
        "pyperclip",
        "jsonschema",
        "pyyaml",
        "pillow",
        "cryptography",
        "certifi",
        "charset-normalizer",
        "idna",
        "urllib3",
        "anyio",
        "sniffio",
        "h11",
        "httpcore",
        "httptools",
        "websockets",
        "watchfiles",
        "python-multipart",
        "starlette",
        "typing-extensions",
        "annotated-types",
        "pydantic-core",
        "packaging",
        "setuptools",
        "wheel"
    ]
    
    # Verificar dependências já instaladas
    print("🔍 Verificando dependências instaladas...")
    installed = []
    missing = []
    
    for dep in dependencies:
        package_name = dep.split("[")[0].replace("-", "_")
        if check_package(package_name):
            installed.append(dep)
        else:
            missing.append(dep)
    
    print(f"✅ Dependências já instaladas: {len(installed)}")
    print(f"❌ Dependências faltando: {len(missing)}")
    
    if not missing:
        print("🎉 Todas as dependências já estão instaladas!")
        return
    
    print("\n📦 Instalando dependências faltando...")
    
    # Atualizar pip primeiro
    print("🔄 Atualizando pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ Pip atualizado com sucesso")
    except subprocess.CalledProcessError:
        print("⚠️ Falha ao atualizar pip, continuando...")
    
    # Instalar dependências
    success_count = 0
    failed_packages = []
    
    for i, package in enumerate(missing, 1):
        print(f"\n📦 [{i}/{len(missing)}] Instalando {package}...")
        
        if install_package(package):
            print(f"✅ {package} instalado com sucesso")
            success_count += 1
        else:
            print(f"❌ Falha ao instalar {package}")
            failed_packages.append(package)
    
    # Relatório final
    print("\n" + "=" * 55)
    print("📊 RELATÓRIO DE INSTALAÇÃO")
    print("=" * 55)
    print(f"✅ Instaladas com sucesso: {success_count}")
    print(f"❌ Falharam: {len(failed_packages)}")
    
    if failed_packages:
        print("\n❌ Pacotes que falharam:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 Tente instalar manualmente:")
        print(f"   pip install {' '.join(failed_packages)}")
    else:
        print("\n🎉 Todas as dependências foram instaladas com sucesso!")
        print("🚀 Agora você pode executar os agentes usando run_agents.py")
    
    print("\n" + "=" * 55)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Instalação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a instalação: {e}")
        print("💡 Tente executar como administrador ou usar um ambiente virtual")