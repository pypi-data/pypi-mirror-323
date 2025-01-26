from setuptools import setup, find_packages

setup(
    name="babot",
    version="0.1.2",
    description="Framework para crear y gestionar agentes inteligentes con modelos locales.",
    author="Kevin Turkienich - Excel-ente",
    packages=find_packages(),
    include_package_data=True,
    license_files=["LICENSE"],
    install_requires=[
        "python-dotenv",
        "langchain-ollama",
        "rich",
        "pypdf",
        "pdf2image",
        "pytesseract"
    ],
    entry_points={
        "console_scripts": [
            "babot=babot.cli:main",  # Asegúrate de que este punto de entrada esté correcto
        ],
    },
)
