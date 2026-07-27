import re
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class DateInfo(TypedDict):
    data_treino: datetime | None
    data: str | None
    horario: str | None
    ano: int | None
    mes: int | None
    dia: int | None


PADRAO_DATA_ARQUIVO = re.compile(
    r"(?P<ano>\d{4})\."
    r"(?P<mes>\d{2})\."
    r"(?P<dia>\d{2})-"
    r"(?P<hora>\d{2})\."
    r"(?P<minuto>\d{2})\."
    r"(?P<segundo>\d{2})"
)


def extrair_data_arquivo(nome_arquivo: str) -> DateInfo:
    """
    Extrai data e horário do nome de um arquivo de treino.

    Exemplo:
    mapa - Challenge - 2025.04.21-20.19.07 Stats.csv
    """

    nome = Path(nome_arquivo).name

    resultado = PADRAO_DATA_ARQUIVO.search(nome)

    if not resultado:
        return {
            "data_treino": None,
            "data": None,
            "horario": None,
            "ano": None,
            "mes": None,
            "dia": None,
        }

    try:
        data_treino = datetime(
            year=int(resultado.group("ano")),
            month=int(resultado.group("mes")),
            day=int(resultado.group("dia")),
            hour=int(resultado.group("hora")),
            minute=int(resultado.group("minuto")),
            second=int(resultado.group("segundo")),
        )

    except ValueError:
        return {
            "data_treino": None,
            "data": None,
            "horario": None,
            "ano": None,
            "mes": None,
            "dia": None,
        }

    return {
        "data_treino": data_treino,
        "data": data_treino.strftime("%Y-%m-%d"),
        "horario": data_treino.strftime("%H:%M:%S"),
        "ano": data_treino.year,
        "mes": data_treino.month,
        "dia": data_treino.day,
    }