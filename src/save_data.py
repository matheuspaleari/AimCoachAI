import pandas as pd

from src.config import HISTORICO_LIMPO_PATH
from src.utils import log_info, log_aviso


def salvar_dados(
    dados: pd.DataFrame,
    caminho=HISTORICO_LIMPO_PATH,
) -> None:
    """
    Salva os dados tratados em CSV.
    """

    if dados.empty:
        log_aviso("Nenhum dado disponível para salvar.")
        return

    caminho.parent.mkdir(parents=True, exist_ok=True)

    dados.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig",
    )

    log_info(f"Dados salvos em: {caminho}")