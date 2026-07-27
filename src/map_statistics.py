import pandas as pd

from src.utils import log_aviso, log_info


COLUNAS_METRICAS = [
    "accuracy_global",
    "ttk_medio",
    "efficiency_media",
    "shots_por_kill",
    "taxa_dano_desperdicado",
    "consistencia_accuracy",
    "consistencia_ttk",
]


def calcular_percentil(
    serie: pd.Series,
    percentil: float,
) -> float | None:
    """
    Calcula um percentil ignorando valores inválidos.
    """

    serie_numerica = pd.to_numeric(
        serie,
        errors="coerce",
    ).dropna()

    if serie_numerica.empty:
        return None

    return round(
        float(serie_numerica.quantile(percentil)),
        6,
    )


def gerar_estatisticas_mapas(
    features: pd.DataFrame,
) -> pd.DataFrame:
    """
    Gera referências estatísticas para cada cenário.

    Cada linha do resultado representa um mapa diferente,
    contendo médias, medianas e percentis das métricas.
    """

    if features.empty:
        log_aviso(
            "Nenhuma feature disponível para gerar "
            "estatísticas dos mapas."
        )
        return pd.DataFrame()

    if "Cenario" not in features.columns:
        log_aviso(
            "A coluna 'Cenario' não foi encontrada nas features."
        )
        return pd.DataFrame()

    colunas_ausentes = [
        coluna
        for coluna in COLUNAS_METRICAS
        if coluna not in features.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível gerar as estatísticas dos mapas. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return pd.DataFrame()

    dados = features.copy()

    for coluna in COLUNAS_METRICAS:
        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors="coerce",
        )

    registros = []

    for cenario, grupo in dados.groupby(
        "Cenario",
        dropna=False,
    ):
        if pd.isna(cenario):
            continue

        registro = {
            "Cenario": cenario,
            "quantidade_treinos": len(grupo),
        }

        if "Categoria" in grupo.columns:
            registro["Categoria"] = grupo[
                "Categoria"
            ].iloc[0]

        if "Subcategoria" in grupo.columns:
            registro["Subcategoria"] = grupo[
                "Subcategoria"
            ].iloc[0]

        for coluna in COLUNAS_METRICAS:
            serie = grupo[coluna]

            registro[f"{coluna}_media"] = round(
                float(serie.mean()),
                6,
            ) if serie.notna().any() else None

            registro[f"{coluna}_mediana"] = round(
                float(serie.median()),
                6,
            ) if serie.notna().any() else None

            registro[f"{coluna}_desvio"] = round(
                float(serie.std()),
                6,
            ) if serie.notna().sum() > 1 else 0.0

            registro[f"{coluna}_p10"] = (
                calcular_percentil(
                    serie,
                    0.10,
                )
            )

            registro[f"{coluna}_p25"] = (
                calcular_percentil(
                    serie,
                    0.25,
                )
            )

            registro[f"{coluna}_p75"] = (
                calcular_percentil(
                    serie,
                    0.75,
                )
            )

            registro[f"{coluna}_p90"] = (
                calcular_percentil(
                    serie,
                    0.90,
                )
            )

            registro[f"{coluna}_min"] = round(
                float(serie.min()),
                6,
            ) if serie.notna().any() else None

            registro[f"{coluna}_max"] = round(
                float(serie.max()),
                6,
            ) if serie.notna().any() else None

        registros.append(registro)

    estatisticas = pd.DataFrame(registros)

    if estatisticas.empty:
        log_aviso(
            "Nenhuma estatística de mapa foi gerada."
        )
        return pd.DataFrame()

    estatisticas = estatisticas.sort_values(
        by="Cenario",
    ).reset_index(drop=True)

    log_info(
        f"Estatísticas geradas para "
        f"{len(estatisticas)} cenário(s)."
    )

    return estatisticas


def obter_estatisticas_cenario(
    estatisticas_mapas: pd.DataFrame,
    cenario: str,
) -> dict:
    """
    Retorna as estatísticas de um cenário específico.
    """

    if estatisticas_mapas.empty:
        return {}

    resultado = estatisticas_mapas[
        estatisticas_mapas["Cenario"] == cenario
    ]

    if resultado.empty:
        return {}

    return resultado.iloc[0].to_dict()


def salvar_estatisticas_mapas(
    estatisticas_mapas: pd.DataFrame,
    caminho: str = "data/processed/map_statistics.csv",
) -> None:
    """
    Salva as referências estatísticas dos mapas em CSV.
    """

    if estatisticas_mapas.empty:
        log_aviso(
            "Nenhuma estatística disponível para salvar."
        )
        return

    caminho_arquivo = pd.io.common.stringify_path(caminho)

    from pathlib import Path

    destino = Path(caminho_arquivo)
    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    estatisticas_mapas.to_csv(
        destino,
        index=False,
        encoding="utf-8-sig",
    )

    log_info(
        f"Estatísticas dos mapas salvas em: {destino}"
    )