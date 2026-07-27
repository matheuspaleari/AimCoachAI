import pandas as pd

from src.utils import log_aviso, log_info


COLUNAS_HABILIDADES = {
    "score_precisao": "Precisão",
    "score_velocidade": "Velocidade",
    "score_controle": "Controle de tiros",
    "score_consistencia": "Consistência",
    "score_geral": "Score Geral",
}


def classificar_tendencia(
    variacao_pontos: float,
    limite: float = 2.0,
) -> str:
    """
    Classifica a tendência usando diferença em pontos.
    """

    if variacao_pontos > limite:
        return "crescente"

    if variacao_pontos < -limite:
        return "decrescente"

    return "estável"


def analisar_performance_cenario(
    scores: pd.DataFrame,
    cenario: str,
    janela_recente: int = 5,
) -> dict:
    """
    Analisa a evolução de um único cenário ao longo do tempo.

    A comparação sempre ocorre entre sessões do mesmo mapa.
    """

    if scores.empty:
        log_aviso(
            "Nenhum score disponível para analisar a performance."
        )
        return {}

    colunas_necessarias = [
        "Cenario",
        "DataTreino",
        *COLUNAS_HABILIDADES.keys(),
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in scores.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível analisar o cenário. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return {}

    dados_cenario = scores[
        scores["Cenario"] == cenario
    ].copy()

    dados_cenario["DataTreino"] = pd.to_datetime(
        dados_cenario["DataTreino"],
        errors="coerce",
    )

    dados_cenario = (
        dados_cenario
        .dropna(subset=["DataTreino"])
        .sort_values("DataTreino")
        .reset_index(drop=True)
    )

    if len(dados_cenario) < 2:
        log_aviso(
            f"O cenário '{cenario}' não possui treinos suficientes "
            "para analisar evolução."
        )
        return {}

    tamanho_janela = min(
        janela_recente,
        max(1, len(dados_cenario) // 2),
    )

    bloco_inicial = dados_cenario.head(
        tamanho_janela
    )

    bloco_recente = dados_cenario.tail(
        tamanho_janela
    )

    habilidades = {}

    for coluna, nome in COLUNAS_HABILIDADES.items():
        media_inicial = bloco_inicial[coluna].mean()
        media_recente = bloco_recente[coluna].mean()

        if pd.isna(media_inicial) or pd.isna(media_recente):
            continue

        variacao_pontos = (
            float(media_recente)
            - float(media_inicial)
        )

        habilidades[coluna] = {
            "nome": nome,
            "media_inicial": round(
                float(media_inicial),
                2,
            ),
            "media_recente": round(
                float(media_recente),
                2,
            ),
            "variacao_pontos": round(
                variacao_pontos,
                2,
            ),
            "tendencia": classificar_tendencia(
                variacao_pontos
            ),
        }

    resultado = {
        "cenario": cenario,
        "quantidade_treinos": len(dados_cenario),
        "janela_comparacao": tamanho_janela,
        "habilidades": habilidades,
    }

    log_info(
        f"Performance analisada para o cenário '{cenario}' "
        f"com {len(dados_cenario)} treino(s)."
    )

    return resultado