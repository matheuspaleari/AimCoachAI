from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_DIR
from src.file_classifier import identificar_tipo_csv
from src.utils import log_aviso, log_erro, log_info


def carregar_dados(pasta: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """
    Carrega apenas arquivos CSV com dados detalhados.

    Arquivos de estatísticas ou formatos desconhecidos
    são ignorados automaticamente.
    """

    pasta.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(pasta.glob("*.csv"))

    if not arquivos:
        log_aviso(f"Nenhum CSV encontrado em: {pasta}")
        return pd.DataFrame()

    dataframes = []

    for arquivo in arquivos:
        tipo_arquivo = identificar_tipo_csv(arquivo)

        if tipo_arquivo == "estatisticas":
            log_aviso(
                f"Arquivo de estatísticas ignorado: "
                f"{arquivo.name}"
            )
            continue

        if tipo_arquivo == "desconhecido":
            log_aviso(
                f"Formato de arquivo desconhecido: "
                f"{arquivo.name}"
            )
            continue

        try:
            dados_arquivo = pd.read_csv(
                arquivo,
                on_bad_lines="skip",
            )

            dados_arquivo["Treino"] = arquivo.stem
            dataframes.append(dados_arquivo)

            log_info(
                f"Arquivo detalhado carregado: "
                f"{arquivo.name} "
                f"({len(dados_arquivo)} registros)"
            )

        except Exception as erro:
            log_erro(
                f"Falha ao carregar {arquivo.name}: "
                f"{erro}"
            )

    if not dataframes:
        log_erro(
            "Nenhum arquivo de dados detalhados pôde ser carregado."
        )
        return pd.DataFrame()

    dados = pd.concat(
        dataframes,
        ignore_index=True,
    )

    log_info(
        f"Total de arquivos detalhados carregados: "
        f"{len(dataframes)}"
    )

    log_info(
        f"Total de registros brutos: "
        f"{len(dados)}"
    )

    return dados