import os
import shutil
import subprocess

# Ruta de la plantilla (estructura base del proyecto)
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template")

def init_project(nombre_proyecto):
    """Inicializa un nuevo proyecto con la estructura base."""
    if os.path.exists(nombre_proyecto):
        print(f"El directorio '{nombre_proyecto}' ya existe. Por favor, elige otro nombre.")
        return

    try:
        # Copiar la plantilla al nuevo directorio
        shutil.copytree(TEMPLATE_PATH, nombre_proyecto)

        # Copiar .env.example a .env
        shutil.copy(os.path.join(nombre_proyecto, ".env.example"), os.path.join(nombre_proyecto, ".env"))

        print(f"Proyecto '{nombre_proyecto}' creado exitosamente.")
        print("Estructura inicial generada. Instala las dependencias con:")
        print(f"\n  cd {nombre_proyecto} && pip install -r requirements.txt")
        print("\nEjecuta el agente Babot con:")
        print(f"\n  babot run babot")
    except Exception as e:
        print(f"Error al crear el proyecto: {e}")


def create_agent(nombre_agente):
    """Crea un nuevo agente dentro del proyecto actual."""
    agentes_dir = "agentes"
    config_dir = "config"

    if not os.path.exists(agentes_dir) or not os.path.exists(config_dir):
        print("Parece que no estás dentro de un proyecto válido. Usa 'babot init' primero.")
        return

    archivo_py = os.path.join(agentes_dir, f"{nombre_agente}.py")
    archivo_yaml = os.path.join(config_dir, f"{nombre_agente}.yaml")

    if os.path.exists(archivo_py) or os.path.exists(archivo_yaml):
        print(f"El agente '{nombre_agente}' ya existe.")
        return

    # Crear plantilla del agente Python
    plantilla_py = f"""
        from langchain_ollama import OllamaLLM
        from rich.console import Console
        from config import Config

        console = Console()

        # Configurar el modelo Ollama
        llm = OllamaLLM(model=Config.OLLAMA_MODEL, base_url=Config.OLLAMA_BASE_URL)

        def ejecutar():
            console.rule("[bold blue]Agente {nombre_agente.capitalize()}[/bold blue]")
            # Lógica del agente aquí
            console.print("[bold green]¡Agente ejecutado exitosamente![/bold green]")

        if __name__ == "__main__":
            ejecutar()
    """
    

    # Crear plantilla YAML
    plantilla_yaml = {
        "descripcion": f"Agente {nombre_agente.capitalize()} generado automáticamente.",
        "parametros": {}
    }

    try:
        with open(archivo_py, "w") as py_file:
            py_file.write(plantilla_py.strip())

        with open(archivo_yaml, "w") as yaml_file:
            import yaml
            yaml.dump(plantilla_yaml, yaml_file, default_flow_style=False, sort_keys=False)

        print(f"Agente '{nombre_agente}' creado exitosamente.")
    except Exception as e:
        print(f"Error al crear el agente: {e}")

def run_agent(nombre_agente):
    """Ejecuta un agente existente."""
    archivo_py = os.path.join("agentes", f"{nombre_agente}.py")
    if not os.path.exists(archivo_py):
        print(f"El agente '{nombre_agente}' no existe.")
        return

    try:
        # Agregar el directorio raíz al PYTHONPATH
        import sys
        sys.path.insert(0, os.getcwd())

        # Usar `python -m` para ejecutar el agente como módulo
        subprocess.run(["python", "-m", f"agentes.{nombre_agente}"])
    except Exception as e:
        print(f"Error al ejecutar el agente: {e}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Babot CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando init
    parser_init = subparsers.add_parser("init", help="Inicializa un nuevo proyecto")
    parser_init.add_argument("nombre_proyecto", help="Nombre del proyecto")

    # Comando create
    parser_create = subparsers.add_parser("create", help="Crea un nuevo agente")
    parser_create.add_argument("nombre_agente", help="Nombre del agente")

    # Comando run
    parser_run = subparsers.add_parser("run", help="Ejecuta un agente existente")
    parser_run.add_argument("nombre_agente", help="Nombre del agente")

    args = parser.parse_args()

    if args.command == "init":
        init_project(args.nombre_proyecto)
    elif args.command == "create":
        create_agent(args.nombre_agente)
    elif args.command == "run":
        run_agent(args.nombre_agente)
    else:
        parser.print_help()
