import pandas as pd

from src.utils import log_aviso, log_info


def obter_janela_historica(
    features: pd.DataFrame,
    quantidade: int = 30,
):
    """
    Separa os treinos em:

    - janela_historica:
        últimos N treinos de cada cenário,
        sem considerar o treino mais recente.

    - treino_atual:
        último treino de cada cenário.
    """

    if features.empty:
        log_aviso(
            "Nenhuma feature disponível para criar a janela histórica."
        )
        return (
            pd.DataFrame(),
            pd.DataFrame(),
        )

    colunas_necessarias = [
        "Cenario",
        "DataTreino",
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in features.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível criar a janela histórica. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return (
            pd.DataFrame(),
            pd.DataFrame(),
        )

    dados = features.copy()

    dados["DataTreino"] = pd.to_datetime(
        dados["DataTreino"],
        errors="coerce",
    )

    dados = dados.dropna(
        subset=[
            "Cenario",
            "DataTreino",
        ]
    )

    dados = dados.sort_values(
        by=[
            "Cenario",
            "DataTreino",
        ]
    )

    historicos = []
    treinos_atuais = []

    for _, grupo in dados.groupby("Cenario"):

        grupo = grupo.sort_values("DataTreino")

        # Se existir apenas um treino,
        # ele será usado como treino atual.
        if len(grupo) == 1:
            treinos_atuais.append(grupo.tail(1))
            continue

        treino_atual = grupo.tail(1)

        historico = grupo.iloc[:-1].tail(quantidade)

        historicos.append(historico)

        treinos_atuais.append(treino_atual)

    if historicos:
        janela = (
            pd.concat(
                historicos,
                ignore_index=True,
            )
        )
    else:
        janela = pd.DataFrame()

    treino_atual = pd.concat(
        treinos_atuais,
        ignore_index=True,
    )

    log_info(
        f"Treinos utilizados como referência: {len(janela)}"
    )

    log_info(
        f"Treinos atuais: {len(treino_atual)}"
    )

    return (
        janela,
        treino_atual,
    )