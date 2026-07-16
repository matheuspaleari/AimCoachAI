import pandas as pd

from src.utils import log_aviso, log_info


def criar_features_treino(dados: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os registros de cada eliminação em um resumo por treino.

    Cada linha do resultado representa um arquivo de treino.
    """

    if dados.empty:
        log_aviso("Nenhum dado disponível para criar features.")
        return pd.DataFrame()

    dados_features = dados.copy()

    colunas_necessarias = [
        "Treino",
        "Timestamp",
        "TTK",
        "Shots",
        "Hits",
        "Accuracy",
        "Damage Done",
        "Damage Possible",
        "Efficiency",
        "OverShots",
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in dados_features.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível criar todas as features. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return pd.DataFrame()

    # Converte o horário para datetime
    dados_features["Timestamp"] = pd.to_datetime(
        dados_features["Timestamp"],
        format="%H:%M:%S.%f",
        errors="coerce",
    )

    # Identifica eliminações sem tiros desperdiçados
    dados_features["Kill_Perfeito"] = (
        dados_features["OverShots"] == 0
    ).astype(int)

    # Calcula a diferença entre o dano possível e o dano realizado
    dados_features["Dano_Desperdicado"] = (
        dados_features["Damage Possible"]
        - dados_features["Damage Done"]
    )

    # Cria um resumo por treino
    resumo = (
        dados_features.groupby("Treino")
        .agg(
            total_kills=("Treino", "size"),

            accuracy_media=("Accuracy", "mean"),
            accuracy_minima=("Accuracy", "min"),
            accuracy_maxima=("Accuracy", "max"),
            accuracy_desvio=("Accuracy", "std"),

            ttk_medio=("TTK", "mean"),
            ttk_minimo=("TTK", "min"),
            ttk_maximo=("TTK", "max"),
            ttk_desvio=("TTK", "std"),

            efficiency_media=("Efficiency", "mean"),
            efficiency_minima=("Efficiency", "min"),
            efficiency_maxima=("Efficiency", "max"),

            total_shots=("Shots", "sum"),
            total_hits=("Hits", "sum"),
            shots_por_kill=("Shots", "mean"),
            hits_por_kill=("Hits", "mean"),

            overshots_total=("OverShots", "sum"),
            overshots_medio=("OverShots", "mean"),

            kills_perfeitos=("Kill_Perfeito", "sum"),

            dano_total=("Damage Done", "sum"),
            dano_possivel_total=("Damage Possible", "sum"),
            dano_desperdicado_total=("Dano_Desperdicado", "sum"),

            inicio_treino=("Timestamp", "min"),
            fim_treino=("Timestamp", "max"),
        )
        .reset_index()
    )

    # Duração do treino em segundos
    resumo["duracao_segundos"] = (
        resumo["fim_treino"] - resumo["inicio_treino"]
    ).dt.total_seconds()

    # Duração do treino em minutos
    resumo["duracao_minutos"] = (
        resumo["duracao_segundos"] / 60
    ).replace(0, pd.NA)

    # Quantidade de eliminações por minuto
    resumo["kills_por_minuto"] = (
        resumo["total_kills"] / resumo["duracao_minutos"]
    )

    # Precisão global com proteção contra divisão por zero
    resumo["accuracy_global"] = (
        resumo["total_hits"]
        / resumo["total_shots"].replace(0, pd.NA)
    )

    # Percentual de eliminações sem tiros desperdiçados
    resumo["percentual_kills_perfeitos"] = (
        resumo["kills_perfeitos"]
        / resumo["total_kills"]
        * 100
    )

    # Consistência da precisão
    # Quanto menor o desvio, mais próximo de 1 será o resultado
    resumo["consistencia_accuracy"] = (
        1 - resumo["accuracy_desvio"].fillna(0)
    ).clip(lower=0, upper=1)

    # Consistência do TTK
    resumo["consistencia_ttk"] = (
        1 / (1 + resumo["ttk_desvio"].fillna(0))
    ).clip(lower=0, upper=1)

    log_info(
        f"Features criadas para {len(resumo)} treino(s)."
    )

    return resumo