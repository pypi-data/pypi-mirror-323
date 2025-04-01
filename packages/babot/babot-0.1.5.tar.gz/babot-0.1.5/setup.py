from setuptools import setup, find_packages

setup(
    name="babot",  # Nombre del paquete
    version="0.1.5",  # Versión inicial
    description="Framework para crear agentes inteligentes personalizados",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Kevin Turkienich",
    author_email="kevin_turkienich@outlook.com",
    url="https://github.com/Excel-ente/babot",  # Repositorio del proyecto
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "babot": [
            "template/*",
            "template/**/*", 
        ],
    },
    install_requires=[
        "rich>=13.9.0",
        "langchain-ollama>=0.2.2",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "pypdf>=5.1.0",
        "pytesseract>=0.3.13",
        "pdf2image>=1.17.0",
    ],
    entry_points={
        "console_scripts": [
            "babot=babot.cli:main",  # CLI principal
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    
)
