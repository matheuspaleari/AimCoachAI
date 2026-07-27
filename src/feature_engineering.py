import pandas as pd

from src.utils import log_aviso, log_info


def criar_features_treino(dados: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os registros de cada eliminação em um resumo por treino.

    Cada linha do resultado representa um arquivo de treino.
    Também preserva as informações de contexto do mapa e da sessão.
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

    # ==========================================================
    # CONVERSÕES E FEATURES AUXILIARES
    # ==========================================================

    dados_features["Timestamp"] = pd.to_datetime(
        dados_features["Timestamp"],
        format="%H:%M:%S.%f",
        errors="coerce",
    )

    dados_features["Kill_Perfeito"] = (
        dados_features["OverShots"] == 0
    ).astype(int)

    dados_features["Dano_Desperdicado"] = (
        dados_features["Damage Possible"]
        - dados_features["Damage Done"]
    )

    # ==========================================================
    # AGREGAÇÕES PRINCIPAIS
    # ==========================================================

    agregacoes = {
        "total_kills": ("Treino", "size"),

        "accuracy_media": ("Accuracy", "mean"),
        "accuracy_minima": ("Accuracy", "min"),
        "accuracy_maxima": ("Accuracy", "max"),
        "accuracy_desvio": ("Accuracy", "std"),

        "ttk_medio": ("TTK", "mean"),
        "ttk_minimo": ("TTK", "min"),
        "ttk_maximo": ("TTK", "max"),
        "ttk_desvio": ("TTK", "std"),

        "efficiency_media": ("Efficiency", "mean"),
        "efficiency_minima": ("Efficiency", "min"),
        "efficiency_maxima": ("Efficiency", "max"),

        "total_shots": ("Shots", "sum"),
        "total_hits": ("Hits", "sum"),
        "shots_por_kill": ("Shots", "mean"),
        "hits_por_kill": ("Hits", "mean"),

        "overshots_total": ("OverShots", "sum"),
        "overshots_medio": ("OverShots", "mean"),

        "kills_perfeitos": ("Kill_Perfeito", "sum"),

        "dano_total": ("Damage Done", "sum"),
        "dano_possivel_total": ("Damage Possible", "sum"),
        "dano_desperdicado_total": (
            "Dano_Desperdicado",
            "sum",
        ),

        "inicio_treino": ("Timestamp", "min"),
        "fim_treino": ("Timestamp", "max"),
    }

    # ==========================================================
    # PRESERVA AS COLUNAS DE CONTEXTO
    # ==========================================================

    colunas_contexto = [
        "Cenario",
        "Categoria",
        "Subcategoria",
        "OrigemClassificacao",
        "DataTreino",
        "Data",
        "Horario",
        "Ano",
        "Mes",
        "Dia",
    ]

    for coluna in colunas_contexto:
        if coluna in dados_features.columns:
            agregacoes[coluna] = (coluna, "first")

    resumo = (
        dados_features.groupby(
            "Treino",
            dropna=False,
        )
        .agg(**agregacoes)
        .reset_index()
    )

    # ==========================================================
    # MÉTRICAS DERIVADAS
    # ==========================================================

    resumo["duracao_segundos"] = (
        resumo["fim_treino"]
        - resumo["inicio_treino"]
    ).dt.total_seconds()

    resumo["duracao_minutos"] = (
        resumo["duracao_segundos"] / 60
    ).replace(0, pd.NA)

    resumo["kills_por_minuto"] = (
        resumo["total_kills"]
        / resumo["duracao_minutos"]
    )

    resumo["accuracy_global"] = (
        resumo["total_hits"]
        / resumo["total_shots"].replace(0, pd.NA)
    )

    # Percentual de dano possível que foi desperdiçado
    resumo["taxa_dano_desperdicado"] = (
        resumo["dano_desperdicado_total"]
        / resumo["dano_possivel_total"].replace(0, pd.NA)
        * 100
    ).fillna(0)

    resumo["percentual_kills_perfeitos"] = (
        resumo["kills_perfeitos"]
        / resumo["total_kills"].replace(0, pd.NA)
        * 100
    )

    resumo["consistencia_accuracy"] = (
        1 - resumo["accuracy_desvio"].fillna(0)
    ).clip(
        lower=0,
        upper=1,
    )

    resumo["consistencia_ttk"] = (
        1 / (1 + resumo["ttk_desvio"].fillna(0))
    ).clip(
        lower=0,
        upper=1,
    )

    # ==========================================================
    # ORDENAÇÃO
    # ==========================================================

    if "DataTreino" in resumo.columns:
        resumo = resumo.sort_values(
            by="DataTreino",
            ascending=True,
            na_position="last",
        ).reset_index(drop=True)

    log_info(
        f"Features criadas para {len(resumo)} treino(s)."
    )

    if "Categoria" in resumo.columns:
        categorias = (
            resumo["Categoria"]
            .value_counts(dropna=False)
            .to_dict()
        )

        log_info(
            f"Treinos por categoria: {categorias}"
        )
    print(resumo.columns.tolist())
    return resumo