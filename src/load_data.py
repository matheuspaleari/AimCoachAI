from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_DIR
from src.utils import log_aviso, log_erro, log_info


def carregar_dados(pasta: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """
    Carrega todos os arquivos CSV encontrados na pasta informada.
    """

    pasta.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(pasta.glob("*.csv"))

    if not arquivos:
        log_aviso(f"Nenhum CSV encontrado em: {pasta}")
        return pd.DataFrame()

    dataframes = []

    for arquivo in arquivos:
        try:
            dados_arquivo = pd.read_csv(
                arquivo,
                on_bad_lines="skip",
            )

            dados_arquivo["Treino"] = arquivo.stem
            dataframes.append(dados_arquivo)

            log_info(
                f"Arquivo carregado: {arquivo.name} "
                f"({len(dados_arquivo)} registros)"
            )

        except Exception as erro:
            log_erro(f"Falha ao carregar {arquivo.name}: {erro}")

    if not dataframes:
        log_erro("Nenhum arquivo pôde ser carregado.")
        return pd.DataFrame()

    dados = pd.concat(dataframes, ignore_index=True)

    log_info(f"Total de arquivos carregados: {len(dataframes)}")
    log_info(f"Total de registros brutos: {len(dados)}")

    return dados