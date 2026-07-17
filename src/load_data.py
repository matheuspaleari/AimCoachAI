from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_DIR
from src.parsers.file_classifier import identificar_tipo_csv
from src.parsers.map_classifier import classificar_mapa
from src.utils import log_aviso, log_erro, log_info


def carregar_dados(pasta: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """
    Carrega todos os arquivos CSV detalhados da pasta.
    Arquivos de estatísticas são ignorados.
    """

    pasta.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(pasta.glob("*.csv"))

    if not arquivos:
        log_aviso(f"Nenhum CSV encontrado em: {pasta}")
        return pd.DataFrame()

    dataframes = []

    for arquivo in arquivos:

        # ==========================================================
        # IDENTIFICA O TIPO DO ARQUIVO
        # ==========================================================

        tipo_arquivo = identificar_tipo_csv(arquivo)

        if tipo_arquivo == "estatisticas":
            log_aviso(
                f"Arquivo de estatísticas ignorado: {arquivo.name}"
            )
            continue

        if tipo_arquivo == "desconhecido":
            log_aviso(
                f"Formato desconhecido: {arquivo.name}"
            )
            continue

        # ==========================================================
        # CARREGA O CSV
        # ==========================================================

        try:

            dados_arquivo = pd.read_csv(
                arquivo,
                on_bad_lines="skip",
            )

            # ======================================================
            # IDENTIFICA O MAPA
            # ======================================================

            mapa = classificar_mapa(arquivo.name)

            dados_arquivo["Treino"] = arquivo.stem
            dados_arquivo["Cenario"] = mapa["cenario"]
            dados_arquivo["Categoria"] = mapa["categoria"]
            dados_arquivo["Subcategoria"] = mapa["subcategoria"]
            dados_arquivo["OrigemClassificacao"] = mapa[
                "origem_classificacao"
            ]

            dataframes.append(dados_arquivo)

            log_info(
                f"{arquivo.name} | "
                f"{mapa['categoria']} | "
                f"{mapa['subcategoria']}"
            )

        except Exception as erro:

            log_erro(
                f"Falha ao carregar {arquivo.name}: {erro}"
            )

    if not dataframes:

        log_erro(
            "Nenhum arquivo detalhado pôde ser carregado."
        )

        return pd.DataFrame()

    dados = pd.concat(
        dataframes,
        ignore_index=True,
    )

    log_info("=" * 50)
    log_info(f"Arquivos carregados: {len(dataframes)}")
    log_info(f"Registros brutos: {len(dados)}")
    log_info("=" * 50)

    return dados