Babot es un framework para crear agentes inteligentes personalizados, integrados con modelos de lenguaje como Llama 2, 
y diseñados para ejecutarse en infraestructura local o en la nube. Ofrece herramientas para inicializar proyectos, 
crear agentes desde cero, clonar agentes predefinidos desde un repositorio, y ejecutar tareas complejas como búsqueda 
en internet o análisis de imágenes.

Características
--------------
- **Fácil Inicialización:** Crea rápidamente un proyecto base con la CLI.
- **Agentes Personalizados:** Diseña agentes con prompts y capacidades específicas.
- **Integración con Ollama:** Utiliza modelos como Llama 2 para respuestas inteligentes.
- **Soporte Modular:** Añade agentes o funcionalidades según las necesidades del negocio.
- **Escalabilidad:** Perfecto para proyectos pequeños o despliegues empresariales.

Instalación
-----------

1. Instala el framework:
pip install babot

2. Verifica que Babot esté instalado:
babot --version


Uso
---
1. **Inicializar un Proyecto**
Para comenzar un nuevo proyecto:
babot init <nombre_proyecto>

Ejemplo:
babot init mi_proyecto

Esto generará una estructura base en el directorio `mi_proyecto`.

2. **Ejecutar un Agente Existente**
Dirígete al directorio del proyecto:
cd <nombre_proyecto>

Ejecuta el agente predeterminado (`babot`):
babot run babot

3. **Modificar el Prompt de un Agente**

Ejecuta el agente nuevamente:
babot run babot

4. **Crear un Nuevo Agente**
Puedes crear un agente desde cero con:
babot create <nombre_agente>

Ejemplo:
babot create agente_ventas

Esto generará:
- Un archivo Python: `agentes/agente_ventas.py`.
- Un archivo de configuración: `config/agente_ventas.yaml`.

Edítalos según tus necesidades y ejecuta el nuevo agente:
babot run agente_ventas

5. **Clonar un Agente desde la Web**
Si deseas usar un agente predefinido de nuestro repositorio, puedes clonarlo:
babot clone <nombre_agente>

Ejemplo:
babot clone agente_marketing

Esto descargará el código del agente y su configuración en tu proyecto.

Ejemplo Completo
----------------
1. Inicializa un nuevo proyecto:
babot init tienda_adema cd tienda_adema

2. Ejecuta el agente predeterminado:
babot run babot

3. Modifica el prompt de Babot para que actúe como un asistente técnico. Edita `config/babot.yaml`:
descripcion: "Asistente técnico para soporte al cliente." prompt_inicial: | Actúa como un soporte técnico para una empresa de tecnología. - Responde preguntas sobre el uso de productos tecnológicos. - Ayuda a los clientes a solucionar problemas comunes. - Mantén un tono claro, amigable y profesional.

4. Ejecuta el agente modificado:
babot run babot

Espero les sirva!

Contribuir
----------
¡Agradecemos tus contribuciones!  
Por favor, abre un issue o un pull request en el repositorio.

Licencia
--------
Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.