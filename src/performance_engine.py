import pandas as pd

from src.utils import log_aviso, log_info


COLUNAS_SCORE = [
    "score_precisao",
    "score_velocidade",
    "score_controle",
    "score_consistencia",
    "score_geral",
]


def calcular_variacao_percentual(
    valor_inicial: float,
    valor_final: float,
) -> float:
    """
    Calcula a variação percentual entre dois valores.
    """

    if pd.isna(valor_inicial) or pd.isna(valor_final):
        return 0.0

    if valor_inicial == 0:
        return 0.0

    variacao = (
        (valor_final - valor_inicial)
        / abs(valor_inicial)
        * 100
    )

    return round(variacao, 2)


def calcular_variacao_pontos(
    valor_inicial: float,
    valor_final: float,
) -> float:
    """
    Calcula a diferença em pontos entre dois valores.
    """

    if pd.isna(valor_inicial) or pd.isna(valor_final):
        return 0.0

    return round(float(valor_final - valor_inicial), 2)


def classificar_tendencia(
    serie: pd.Series,
    janela_media: int = 5,
    limite_pontos: float = 2.0,
) -> str:
    """
    Classifica a tendência como crescente, estável ou decrescente.

    Compara a média do início da janela com a média do fim da janela.
    Pequenas oscilações dentro do limite são consideradas estáveis.
    """

    serie = serie.dropna().astype(float)

    if len(serie) < 4:
        return "dados insuficientes"

    tamanho_bloco = min(
        janela_media,
        max(2, len(serie) // 3),
    )

    media_inicial = serie.head(tamanho_bloco).mean()
    media_final = serie.tail(tamanho_bloco).mean()

    diferenca = media_final - media_inicial

    if diferenca > limite_pontos:
        return "crescente"

    if diferenca < -limite_pontos:
        return "decrescente"

    return "estável"


def analisar_habilidade(
    dados: pd.DataFrame,
    coluna: str,
    janela: int = 15,
) -> dict:
    """
    Analisa o histórico completo e a tendência recente
    de uma habilidade.
    """

    serie_completa = dados[coluna].dropna().astype(float)

    if serie_completa.empty:
        return {
            "score_atual": 0.0,
            "media_historica": 0.0,
            "media_recente": 0.0,
            "melhor_score": 0.0,
            "pior_score": 0.0,
            "variacao_total_percentual": 0.0,
            "variacao_total_pontos": 0.0,
            "diferenca_media_historica": 0.0,
            "tendencia_recente": "dados insuficientes",
        }

    serie_recente = serie_completa.tail(janela)

    score_atual = float(serie_completa.iloc[-1])
    score_inicial = float(serie_completa.iloc[0])
    media_historica = float(serie_completa.mean())
    media_recente = float(serie_recente.mean())

    return {
        "score_atual": round(score_atual, 2),
        "media_historica": round(media_historica, 2),
        "media_recente": round(media_recente, 2),
        "melhor_score": round(float(serie_completa.max()), 2),
        "pior_score": round(float(serie_completa.min()), 2),
        "variacao_total_percentual": calcular_variacao_percentual(
            score_inicial,
            score_atual,
        ),
        "variacao_total_pontos": calcular_variacao_pontos(
            score_inicial,
            score_atual,
        ),
        "diferenca_media_historica": round(
            media_recente - media_historica,
            2,
        ),
        "tendencia_recente": classificar_tendencia(
            serie_recente,
            janela_media=5,
            limite_pontos=2.0,
        ),
    }


def analisar_performance(
    scores: pd.DataFrame,
    janela: int = 15,
) -> dict:
    """
    Analisa a evolução do jogador ao longo dos treinos.
    """

    if scores.empty:
        log_aviso("Nenhum score disponível para análise de performance.")
        return {}

    colunas_ausentes = [
        coluna
        for coluna in COLUNAS_SCORE
        if coluna not in scores.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível analisar a performance. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return {}

    analise = {
        "precisao": analisar_habilidade(
            scores,
            "score_precisao",
            janela,
        ),
        "velocidade": analisar_habilidade(
            scores,
            "score_velocidade",
            janela,
        ),
        "controle": analisar_habilidade(
            scores,
            "score_controle",
            janela,
        ),
        "consistencia": analisar_habilidade(
            scores,
            "score_consistencia",
            janela,
        ),
        "geral": analisar_habilidade(
            scores,
            "score_geral",
            janela,
        ),
    }

    treino_melhor = scores.loc[
        scores["score_geral"].idxmax()
    ]

    treino_pior = scores.loc[
        scores["score_geral"].idxmin()
    ]

    habilidades_atuais = {
        "Precisão": analise["precisao"]["score_atual"],
        "Velocidade": analise["velocidade"]["score_atual"],
        "Controle de tiros": analise["controle"]["score_atual"],
        "Consistência": analise["consistencia"]["score_atual"],
    }

    principal_ponto_atual = min(
        habilidades_atuais,
        key=habilidades_atuais.get,
    )

    habilidades_em_queda = [
        habilidade
        for habilidade, dados_habilidade in analise.items()
        if habilidade != "geral"
        and dados_habilidade["tendencia_recente"] == "decrescente"
    ]

    analise["resumo"] = {
        "treino_atual": scores.iloc[-1]["Treino"],
        "melhor_treino": treino_melhor["Treino"],
        "melhor_score_geral": round(
            float(treino_melhor["score_geral"]),
            2,
        ),
        "pior_treino": treino_pior["Treino"],
        "pior_score_geral": round(
            float(treino_pior["score_geral"]),
            2,
        ),
        "principal_ponto_atual": principal_ponto_atual,
        "habilidades_em_queda": habilidades_em_queda,
    }

    log_info(
        f"Performance analisada com base em {len(scores)} treino(s)."
    )

    return analise