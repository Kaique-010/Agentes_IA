"""
Script para executar diferentes agentes do sistema
"""
import sys
import asyncio
import subprocess
import os

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import langchain
        import langgraph
        import fastapi
        import uvicorn
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("📦 Execute: python install_dependencies.py")
        return False

def show_menu():
    print("🤖 Sistema de Agentes IA")
    print("=" * 35)
    print("1. 🔗 Agente Integração ML (Web)")
    print("2. 👨‍💻 Agente Programador (Web)")
    print("3. 💰 Agente Binance (Web)")
    print("4. 🎯 Agente Bet365 (Web)")
    print("5. 🔗 Agente Integração ML (Terminal)")
    print("6. 👨‍💻 Agente Programador (Terminal)")
    print("7. 💰 Agente Binance (Terminal)")
    print("8. 🎯 Agente Bet365 (Terminal)")
    print("9. 📦 Instalar Dependências")
    print("0. ❌ Sair")
    print("=" * 35)

def run_web_server(server_file, port):
    """Executa um servidor web"""
    try:
        print(f"🌐 Servidor disponível em: http://localhost:{port}")
        subprocess.run([sys.executable, "-m", "uvicorn", f"{server_file}:app", "--reload", "--port", str(port)])
    except KeyboardInterrupt:
        print(f"\n🛑 Servidor {server_file} encerrado")
    except Exception as e:
        print(f"❌ Erro ao executar servidor: {e}")

def run_terminal_agent(agent_file):
    """Executa um agente no terminal"""
    try:
        subprocess.run([sys.executable, agent_file])
    except KeyboardInterrupt:
        print(f"\n🛑 Agente {agent_file} encerrado")
    except Exception as e:
        print(f"❌ Erro ao executar agente: {e}")

def install_dependencies():
    """Executa o script de instalação de dependências"""
    try:
        subprocess.run([sys.executable, "install_dependencies.py"])
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")

def main():
    print("🚀 Iniciando Sistema de Agentes IA...")
    
    while True:
        show_menu()
        choice = input("Escolha uma opção: ").strip()
        
        if choice == "1":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Integração ML (Web) na porta 8000...")
            run_web_server("app", 8000)
            
        elif choice == "2":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Programador (Web) na porta 8001...")
            run_web_server("server", 8001)
            
        elif choice == "3":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Binance (Web) na porta 8002...")
            run_web_server("binance_server", 8002)
            
        elif choice == "4":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Bet365 (Web) na porta 8003...")
            run_web_server("bet365_server", 8003)
            
        elif choice == "5":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Integração ML (Terminal)...")
            run_terminal_agent("main.py")
            
        elif choice == "6":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Programador (Terminal)...")
            run_terminal_agent("dev_main.py")
            
        elif choice == "7":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Binance (Terminal)...")
            run_terminal_agent("binance_main.py")
            
        elif choice == "8":
            if not check_dependencies():
                continue
            print("🚀 Iniciando Agente Bet365 (Terminal)...")
            run_terminal_agent("bet365_main.py")
            
        elif choice == "9":
            print("📦 Instalando dependências...")
            install_dependencies()
            
        elif choice == "0":
            print("👋 Encerrando sistema...")
            break
            
        else:
            print("❌ Opção inválida!")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()