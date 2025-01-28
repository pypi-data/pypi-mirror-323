from langchain_ollama import OllamaLLM
from rich.console import Console
from config_base import Config
import yaml
import os

console = Console()

# Configurar el modelo Ollama
llm = OllamaLLM(
    model=Config.OLLAMA_MODEL,
    base_url=Config.OLLAMA_BASE_URL,
    temperature=Config.OLLAMA_TEMPERATURE,
    top_p=Config.OLLAMA_TOP_P,
)

# Cargar la configuración del YAML
def cargar_configuracion(nombre_agente):
    ruta_config = os.path.join("config", f"{nombre_agente}.yaml")
    with open(ruta_config, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

# Limpiar etiquetas <think>
def limpiar_respuesta(respuesta):
    return respuesta.replace("<think>", "").replace("</think>", "").strip()

def chat():
    """Chat interactivo con el modelo configurado."""
    console.rule("[bold blue]Babot - Chat Interactivo[/bold blue]")

    # Cargar configuración del YAML
    config_babot = cargar_configuracion("babot")
    prompt_inicial = config_babot.get("prompt_inicial", "")
    console.print(f"[bold yellow]Prompt inicial cargado:[/bold yellow] {prompt_inicial}\n")

    # Inicia el chat
    while True:
        user_input = console.input("[bold green]Tú:[/bold green] ")
        if user_input.lower() in ["salir", "exit"]:
            console.print("[bold red]Saliendo del chat...[/bold red]")
            break
        try:
            # Combina el prompt inicial con el mensaje del usuario
            full_prompt = f"{prompt_inicial}\n\nCliente: {user_input}"
            response = llm.invoke(full_prompt)
            clean_response = limpiar_respuesta(response)
            console.print(f"[bold yellow]Babot:[/bold yellow] {clean_response}")
        except Exception as e:
            console.print(f"[bold red]Error al procesar tu mensaje: {e}[/bold red]")

if __name__ == "__main__":
    chat()
