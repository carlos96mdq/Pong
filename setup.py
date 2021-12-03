import sys
from cx_Freeze import setup, Executable

setup(
    name = "Pong",
    version = "0.5",
    description = "Juego de Pong",
    executables = [Executable("principal.py")])