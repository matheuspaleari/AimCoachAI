import pandas as pd

from src.map_statistics import gerar_estatisticas_mapas
from src.utils import log_aviso, log_info


COLUNAS_SCORE = [
    "score_precisao",
    "score_velocidade",
    "score_controle",
    "score_consistencia",
]

MINIMO_TREINOS_REFERENCIA = 5


def limitar_score(valor: float) -> float:
    """
    Mantém o score entre 0 e 100.

    Valores ausentes recebem 50 apenas quando existe histórico
    suficiente, mas a métrica não possui variação estatística.
    """

    if pd.isna(valor):
        return 50.0

    return round(
        max(0.0, min(100.0, float(valor))),
        2,
    )


def normalizar_por_referencia(
    valor: float,
    referencia_media: float,
    referencia_desvio: float,
    maior_melhor: bool = True,
) -> float:
    """
    Calcula o score em relação ao histórico do próprio cenário.

    Regras:
    - desempenho médio equivale a 60 pontos;
    - evolução acima da média recebe bônus maior;
    - desempenho abaixo da média sofre uma penalização menor;
    - o score fica entre 10 e 98 pontos.
    """

    if (
        pd.isna(valor)
        or pd.isna(referencia_media)
        or pd.isna(referencia_desvio)
    ):
        return 60.0

    valor = float(valor)
    media = float(referencia_media)
    desvio = float(referencia_desvio)

    if abs(desvio) < 1e-9:
        return 60.0

    z_score = (valor - media) / desvio

    if not maior_melhor:
        z_score = -z_score

    # Acima da média: progressão mais visível
    if z_score >= 0:
        score = 60 + (z_score * 18)

    # Abaixo da média: penalização mais suave
    else:
        score = 60 + (z_score * 10)

    return limitar_score(
        max(10.0, min(98.0, score))
    )


def calcular_score_precisao(
    linha: pd.Series,
) -> float:
    """
    Quanto maior a precisão global, melhor.
    """

    return normalizar_por_referencia(
        valor=linha["accuracy_global"],
        referencia_media=linha["accuracy_global_media"],
        referencia_desvio=linha["accuracy_global_desvio"],
        maior_melhor=True,
    )


def calcular_score_velocidade(
    linha: pd.Series,
) -> float:
    """
    Quanto menor o TTK médio, melhor.
    """

    return normalizar_por_referencia(
        valor=linha["ttk_medio"],
        referencia_media=linha["ttk_medio_media"],
        referencia_desvio=linha["ttk_medio_desvio"],
        maior_melhor=False,
    )


def calcular_score_controle(
    linha: pd.Series,
) -> float:
    """
    Avalia o controle dos disparos usando métricas
    que realmente variam entre os treinos.
    """

    score_eficiencia = normalizar_por_referencia(
        valor=linha["efficiency_media"],
        referencia_media=linha["efficiency_media_media"],
        referencia_desvio=linha["efficiency_media_desvio"],
        maior_melhor=True,
    )

    score_shots = normalizar_por_referencia(
        valor=linha["shots_por_kill"],
        referencia_media=linha["shots_por_kill_media"],
        referencia_desvio=linha["shots_por_kill_desvio"],
        maior_melhor=False,
    )

    score_dano = normalizar_por_referencia(
        valor=linha["taxa_dano_desperdicado"],
        referencia_media=linha["taxa_dano_desperdicado_media"],
        referencia_desvio=linha["taxa_dano_desperdicado_desvio"],
        maior_melhor=False,
    )

    score = (
        score_eficiencia * 0.40
        + score_shots * 0.30
        + score_dano * 0.30
    )

    return limitar_score(score)


def calcular_score_consistencia(
    linha: pd.Series,
) -> float:
    """
    Combina a consistência da precisão e do TTK.
    """

    score_accuracy = normalizar_por_referencia(
        valor=linha["consistencia_accuracy"],
        referencia_media=linha[
            "consistencia_accuracy_media"
        ],
        referencia_desvio=linha[
            "consistencia_accuracy_desvio"
        ],
        maior_melhor=True,
    )

    score_ttk = normalizar_por_referencia(
        valor=linha["consistencia_ttk"],
        referencia_media=linha[
            "consistencia_ttk_media"
        ],
        referencia_desvio=linha[
            "consistencia_ttk_desvio"
        ],
        maior_melhor=True,
    )

    score = (
        score_accuracy * 0.60
        + score_ttk * 0.40
    )

    return limitar_score(score)


def calcular_scores(
    features: pd.DataFrame,
    estatisticas_mapas: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Calcula scores usando referências estatísticas
    específicas de cada cenário.

    Cenários com menos de cinco treinos anteriores recebem
    scores ausentes, evitando que a falta de histórico seja
    apresentada como uma avaliação neutra de 50 pontos.
    """

    if features.empty:
        log_aviso(
            "Nenhuma feature disponível para calcular scores."
        )
        return pd.DataFrame()

    colunas_necessarias = [
        "Cenario",
        "accuracy_global",
        "ttk_medio",
        "efficiency_media",
        "shots_por_kill",
        "taxa_dano_desperdicado",
        "consistencia_accuracy",
        "consistencia_ttk",
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in features.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível calcular os scores. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return pd.DataFrame()

    if (
        estatisticas_mapas is None
        or estatisticas_mapas.empty
    ):
        estatisticas_mapas = gerar_estatisticas_mapas(
            features
        )

    if estatisticas_mapas.empty:
        log_aviso(
            "Não foi possível gerar referências estatísticas "
            "para os cenários."
        )
        return pd.DataFrame()

    colunas_referencia = [
        "Cenario",
        "quantidade_treinos",
        "accuracy_global_media",
        "accuracy_global_desvio",
        "ttk_medio_media",
        "ttk_medio_desvio",
        "efficiency_media_media",
        "efficiency_media_desvio",
        "shots_por_kill_media",
        "shots_por_kill_desvio",
        "taxa_dano_desperdicado_media",
        "taxa_dano_desperdicado_desvio",
        "consistencia_accuracy_media",
        "consistencia_accuracy_desvio",
        "consistencia_ttk_media",
        "consistencia_ttk_desvio",
    ]

    referencias_ausentes = [
        coluna
        for coluna in colunas_referencia
        if coluna not in estatisticas_mapas.columns
    ]

    if referencias_ausentes:
        log_aviso(
            "As estatísticas dos mapas estão incompletas. "
            f"Colunas ausentes: {', '.join(referencias_ausentes)}"
        )
        return pd.DataFrame()

    referencias = estatisticas_mapas[
        colunas_referencia
    ].copy()

    dados_scores = features.merge(
        referencias,
        on="Cenario",
        how="left",
        validate="many_to_one",
    )

    dados_scores["historico_suficiente"] = (
        dados_scores["quantidade_treinos"]
        .fillna(0)
        .ge(MINIMO_TREINOS_REFERENCIA)
    )

    dados_scores["score_precisao"] = dados_scores.apply(
        calcular_score_precisao,
        axis=1,
    )

    dados_scores["score_velocidade"] = dados_scores.apply(
        calcular_score_velocidade,
        axis=1,
    )

    dados_scores["score_controle"] = dados_scores.apply(
        calcular_score_controle,
        axis=1,
    )

    dados_scores["score_consistencia"] = dados_scores.apply(
        calcular_score_consistencia,
        axis=1,
    )

    dados_scores[COLUNAS_SCORE] = (
        dados_scores[COLUNAS_SCORE]
        .clip(lower=0, upper=100)
        .round(2)
    )

    sem_historico = ~dados_scores["historico_suficiente"]

    dados_scores.loc[
        sem_historico,
        COLUNAS_SCORE,
    ] = pd.NA

    dados_scores["score_geral"] = (
        dados_scores[COLUNAS_SCORE]
        .mean(axis=1)
        .round(2)
    )

    dados_scores.loc[
        sem_historico,
        "score_geral",
    ] = pd.NA

    quantidade_sem_historico = int(
        sem_historico.sum()
    )

    colunas_temporarias = [
        coluna
        for coluna in colunas_referencia
        if coluna != "Cenario"
    ]

    dados_scores = dados_scores.drop(
        columns=colunas_temporarias,
        errors="ignore",
    )

    log_info(
        "Scores calculados com referências estatísticas "
        f"para {len(dados_scores)} treino(s)."
    )

    if quantidade_sem_historico:
        log_aviso(
            f"{quantidade_sem_historico} treino(s) ficaram sem score "
            f"por possuírem menos de "
            f"{MINIMO_TREINOS_REFERENCIA} referências no cenário."
        )

    dados_validos = dados_scores[
        dados_scores["historico_suficiente"]
    ]

    if not dados_validos.empty:
        log_info(
            "Médias dos scores válidos: "
            f"Precisão={dados_validos['score_precisao'].mean():.2f}, "
            f"Velocidade={dados_validos['score_velocidade'].mean():.2f}, "
            f"Controle={dados_validos['score_controle'].mean():.2f}, "
            f"Consistência="
            f"{dados_validos['score_consistencia'].mean():.2f}."
        )

    return dados_scores
