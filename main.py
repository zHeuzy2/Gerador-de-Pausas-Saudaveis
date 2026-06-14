"""Ponto de entrada do Gerador de Pausas Saudáveis."""

import os
import sys

# Garante que o pacote src/ esteja no caminho de importação.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from app import main  # noqa: E402

if __name__ == "__main__":
    main()
