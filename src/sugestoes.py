"""Carregamento e sorteio das sugestões saudáveis a partir do sugestoes.json."""

from __future__ import annotations

import json
import random
from pathlib import Path

_CAMINHO = Path(__file__).parent / "data" / "sugestoes.json"


def carregar_sugestoes() -> dict[str, list[dict]]:
    """Lê o arquivo de sugestões e devolve o dicionário por tipo de pausa."""
    with open(_CAMINHO, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def sortear_sugestao(dados: dict[str, list[dict]]) -> dict:
    """Sorteia uma sugestão aleatória misturando todos os tipos de pausa.

    Devolve um dicionário com ``titulo``, ``descricao``, ``icon`` e ``tipo``.
    """
    tipos = [t for t, itens in dados.items() if itens]
    if not tipos:
        return {
            "titulo": "Faça uma pausa",
            "descricao": "Levante, respire e descanse a vista.",
            "icon": "🌿",
            "tipo": "geral",
        }
    tipo = random.choice(tipos)
    sugestao = dict(random.choice(dados[tipo]))
    sugestao["tipo"] = tipo
    return sugestao
