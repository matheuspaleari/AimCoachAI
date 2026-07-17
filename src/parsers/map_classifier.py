"""
Classificação e normalização dos mapas do AimCoachAI.
"""

import re
from pathlib import Path
from typing import TypedDict

from src.parsers.map_catalog import MAP_CATALOG


class MapClassification(TypedDict):
    cenario: str
    categoria: str
    subcategoria: str
    origem_classificacao: str


def limpar_nome_cenario(nome_arquivo: str) -> str:
    """
    Remove extensão, data, horário e os sufixos gerados pelo Aim Trainer.
    """

    nome = Path(nome_arquivo).stem

    nome = re.sub(
        r"\s*-\s*Challenge\s*-\s*"
        r"\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}"
        r"\s*Stats$",
        "",
        nome,
        flags=re.IGNORECASE,
    )

    nome = re.sub(
        r"\s+Stats$",
        "",
        nome,
        flags=re.IGNORECASE,
    )

    return " ".join(nome.split()).strip()


def classificar_por_regras(nome_cenario: str) -> tuple[str, str]:
    """
    Classificação de fallback para mapas que ainda não estejam no catálogo.
    """

    nome = nome_cenario.casefold()

    termos_target_switching = (
        "target switch",
        "targetswitch",
        "switching",
        "beants",
        "waldots",
        "domiswitch",
    )

    if (
        any(termo in nome for termo in termos_target_switching)
        or re.search(r"\bww\d", nome)
        or re.search(r"\b\d+w\d+ts\b", nome)
    ):
        if any(
            termo in nome
            for termo in ("small", "micro", "precise", "static")
        ):
            return "Target Switching", "Precisão"

        return "Target Switching", "Velocidade"

    termos_tracking = (
        "track",
        "tracking",
        "smoothbot",
        "smoothsphere",
        "controlsphere",
        "rawcontrol",
        "raw control",
        "rawmousecontrol",
        "whisphere",
        "preciseorb",
        "ground plaza",
        "leapstrafe",
        "leaptrack",
        "strafes",
        "air ",
        "adjusttrack",
    )

    if any(termo in nome for termo in termos_tracking):
        if any(
            termo in nome
            for termo in ("reactive", "air ", "ground plaza", "strafes", "leap")
        ):
            return "Tracking", "Reativo"

        if any(
            termo in nome
            for termo in ("precise", "control", "adjust", "raw")
        ):
            return "Tracking", "Precisão e controle"

        return "Tracking", "Suave"

    termos_clicking_dinamico = (
        "pasu",
        "bounce",
        "popcorn",
        "floating",
        "penta",
        "moving",
        "frogtagon",
    )

    if any(termo in nome for termo in termos_clicking_dinamico):
        return "Clicking", "Dinâmico"

    return "Clicking", "Estático e flick"


def classificar_mapa(nome_arquivo: str) -> MapClassification:
    """
    Classifica um mapa usando primeiro o catálogo oficial.

    Se o mapa ainda não existir no catálogo, utiliza regras de fallback.
    """

    cenario = limpar_nome_cenario(nome_arquivo)

    classificacao_catalogo = MAP_CATALOG.get(cenario)

    if classificacao_catalogo:
        return {
            "cenario": cenario,
            "categoria": classificacao_catalogo["categoria"],
            "subcategoria": classificacao_catalogo["subcategoria"],
            "origem_classificacao": "catalogo",
        }

    categoria, subcategoria = classificar_por_regras(cenario)

    return {
        "cenario": cenario,
        "categoria": categoria,
        "subcategoria": subcategoria,
        "origem_classificacao": "regras",
    }
