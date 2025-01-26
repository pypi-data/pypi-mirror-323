from setuptools import setup, find_packages

setup(
    name="Generador",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "tkinter",  # Añade aquí todas las dependencias necesarias
    ],
    entry_points={
        "console_scripts": [
            "generador=Generador.main:main",  # Ajusta esto según tu punto de entrada
        ],
    },
)