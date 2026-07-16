import pandas as pd

from src.utils import log_aviso, log_info


def limitar_score(valor: float) -> float:
    """
    Mantém o score entre 0 e 100.
    """
    return round(max(0, min(100, valor)), 2)


def calcular_score_precisao(accuracy: float) -> float:
    """
    Converte a Accuracy, normalmente entre 0 e 1,
    em uma nota de 0 a 100.
    """

    if pd.isna(accuracy):
        return 0.0

    return limitar_score(accuracy * 100)


def calcular_score_velocidade(ttk: float) -> float:
    """
    Quanto menor o TTK, maior o score.

    Referência inicial:
    - TTK de 0,20s ou menor: 100 pontos
    - TTK de 1,00s ou maior: 0 pontos
    """

    if pd.isna(ttk):
        return 0.0

    ttk_melhor = 0.20
    ttk_pior = 1.00

    score = (
        (ttk_pior - ttk)
        / (ttk_pior - ttk_melhor)
        * 100
    )

    return limitar_score(score)


def calcular_score_controle(
    overshots_medio: float,
    percentual_kills_perfeitos: float,
) -> float:
    """
    Avalia o controle dos disparos.

    Combina:
    - quantidade média de overshots;
    - percentual de eliminações sem tiros extras.
    """

    if pd.isna(overshots_medio):
        overshots_medio = 0

    if pd.isna(percentual_kills_perfeitos):
        percentual_kills_perfeitos = 0

    score_overshots = 100 - (overshots_medio * 15)
    score_kills_perfeitos = percentual_kills_perfeitos

    score = (
        score_overshots * 0.6
        + score_kills_perfeitos * 0.4
    )

    return limitar_score(score)


def calcular_score_consistencia(
    consistencia_accuracy: float,
    consistencia_ttk: float,
) -> float:
    """
    Combina a consistência da precisão e do TTK.
    """

    if pd.isna(consistencia_accuracy):
        consistencia_accuracy = 0

    if pd.isna(consistencia_ttk):
        consistencia_ttk = 0

    score = (
        consistencia_accuracy * 100 * 0.6
        + consistencia_ttk * 100 * 0.4
    )

    return limitar_score(score)


def calcular_scores(features: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona scores de habilidade ao resumo de cada treino.
    """

    if features.empty:
        log_aviso("Nenhuma feature disponível para calcular scores.")
        return pd.DataFrame()

    dados_scores = features.copy()

    dados_scores["score_precisao"] = dados_scores[
        "accuracy_global"
    ].apply(calcular_score_precisao)

    dados_scores["score_velocidade"] = dados_scores[
        "ttk_medio"
    ].apply(calcular_score_velocidade)

    dados_scores["score_controle"] = dados_scores.apply(
        lambda linha: calcular_score_controle(
            linha["overshots_medio"],
            linha["percentual_kills_perfeitos"],
        ),
        axis=1,
    )

    dados_scores["score_consistencia"] = dados_scores.apply(
        lambda linha: calcular_score_consistencia(
            linha["consistencia_accuracy"],
            linha["consistencia_ttk"],
        ),
        axis=1,
    )

    colunas_score = [
        "score_precisao",
        "score_velocidade",
        "score_controle",
        "score_consistencia",
    ]

    dados_scores["score_geral"] = (
        dados_scores[colunas_score].mean(axis=1)
    ).round(2)

    log_info(
        f"Scores calculados para {len(dados_scores)} treino(s)."
    )

    return dados_scores