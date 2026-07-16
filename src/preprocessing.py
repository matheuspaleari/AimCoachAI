import pandas as pd

from src.config import COLUNAS_NUMERICAS, COLUNAS_OBRIGATORIAS
from src.utils import log_aviso, log_info


def validar_colunas(df: pd.DataFrame) -> list[str]:
    """
    Retorna uma lista com as colunas obrigatórias que não foram encontradas.
    """

    return [
        coluna
        for coluna in COLUNAS_OBRIGATORIAS
        if coluna not in df.columns
    ]


def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa, valida e padroniza os dados enviados pelo jogador.
    """

    if df.empty:
        return df

    dados = df.copy()

    dados.columns = dados.columns.str.strip()

    colunas_ausentes = validar_colunas(dados)

    if colunas_ausentes:
        log_aviso(
            "Colunas ausentes: "
            + ", ".join(colunas_ausentes)
        )

    registros_iniciais = len(dados)

    dados = dados.dropna(how="all")
    dados = dados.drop_duplicates()

    if "TTK" in dados.columns:
        dados["TTK"] = (
            dados["TTK"]
            .astype(str)
            .str.strip()
            .str.replace("s", "", regex=False)
        )

        dados["TTK"] = pd.to_numeric(
            dados["TTK"],
            errors="coerce",
        )

    for coluna in COLUNAS_NUMERICAS:
        if coluna in dados.columns:
            dados[coluna] = pd.to_numeric(
                dados[coluna],
                errors="coerce",
            )

    colunas_principais = [
        coluna
        for coluna in ["Accuracy", "Efficiency", "TTK"]
        if coluna in dados.columns
    ]

    if colunas_principais:
        dados = dados.dropna(subset=colunas_principais)

    dados = dados.reset_index(drop=True)

    removidos = registros_iniciais - len(dados)

    log_info(f"Registros removidos durante a limpeza: {removidos}")
    log_info(f"Registros válidos: {len(dados)}")

    return dados