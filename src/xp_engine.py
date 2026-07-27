import pandas as pd

from src.utils import log_aviso, log_info


XP_BASE_POR_TREINO = 100


def calcular_xp_treino(
    score_geral: float,
    score_consistencia: float,
) -> int:
    """
    Calcula o XP obtido em um treino.

    Regras:
    - todo treino concede XP base;
    - score geral aumenta o XP;
    - consistência concede bônus adicional;
    - o XP nunca é negativo.
    """

    if pd.isna(score_geral):
        score_geral = 0

    if pd.isna(score_consistencia):
        score_consistencia = 0

    bonus_desempenho = score_geral * 1.5
    bonus_consistencia = score_consistencia * 0.5

    xp = (
        XP_BASE_POR_TREINO
        + bonus_desempenho
        + bonus_consistencia
    )

    return max(0, round(xp))


def calcular_xp_jogador(
    scores: pd.DataFrame,
) -> dict:
    """
    Calcula o XP acumulado do jogador.

    Usa apenas registros com score válido.
    """

    if scores.empty:
        log_aviso(
            "Nenhum score disponível para calcular XP."
        )
        return {}

    colunas_necessarias = [
        "score_geral",
        "score_consistencia",
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in scores.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível calcular XP. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return {}

    dados_validos = scores.dropna(
        subset=colunas_necessarias,
    ).copy()

    if dados_validos.empty:
        log_aviso(
            "Nenhum treino válido disponível para calcular XP."
        )
        return {}

    dados_validos["xp_treino"] = dados_validos.apply(
        lambda linha: calcular_xp_treino(
            score_geral=linha["score_geral"],
            score_consistencia=linha["score_consistencia"],
        ),
        axis=1,
    )

    xp_total = int(
        dados_validos["xp_treino"].sum()
    )

    quantidade_treinos = len(dados_validos)

    xp_medio = round(
        xp_total / quantidade_treinos,
    )

    resultado = {
        "xp_total": xp_total,
        "xp_medio_por_treino": xp_medio,
        "quantidade_treinos": quantidade_treinos,
    }

    log_info(
        f"XP calculado: {xp_total} pontos em "
        f"{quantidade_treinos} treino(s)."
    )

    return resultado

FAIXAS_XP = [
    {
        "elo": "⚙️ Ferro",
        "xp_minimo": 0,
        "xp_proximo": 5_000,
    },
    {
        "elo": "🟤 Bronze",
        "xp_minimo": 5_000,
        "xp_proximo": 12_000,
    },
    {
        "elo": "⚪ Prata",
        "xp_minimo": 12_000,
        "xp_proximo": 22_000,
    },
    {
        "elo": "🟡 Ouro",
        "xp_minimo": 22_000,
        "xp_proximo": 36_000,
    },
    {
        "elo": "🔷 Platina",
        "xp_minimo": 36_000,
        "xp_proximo": 55_000,
    },
    {
        "elo": "💎 Diamante",
        "xp_minimo": 55_000,
        "xp_proximo": 80_000,
    },
    {
        "elo": "🟢 Ascendente",
        "xp_minimo": 80_000,
        "xp_proximo": 115_000,
    },
    {
        "elo": "🔴 Imortal",
        "xp_minimo": 115_000,
        "xp_proximo": 160_000,
    },
    {
        "elo": "☀️ Radiante",
        "xp_minimo": 160_000,
        "xp_proximo": None,
    },
]


def obter_progresso_xp(
    xp_total: int,
) -> dict:
    """
    Retorna o elo de XP, progresso atual
    e quantidade necessária para o próximo elo.
    """

    faixa_atual = FAIXAS_XP[0]

    for faixa in FAIXAS_XP:
        if xp_total >= faixa["xp_minimo"]:
            faixa_atual = faixa
        else:
            break

    xp_minimo = faixa_atual["xp_minimo"]
    xp_proximo = faixa_atual["xp_proximo"]

    if xp_proximo is None:
        return {
            "elo_xp": faixa_atual["elo"],
            "xp_atual_faixa": xp_total - xp_minimo,
            "xp_necessario_faixa": 0,
            "xp_faltante": 0,
            "progresso": 1.0,
            "nivel_maximo": True,
        }

    xp_atual_faixa = xp_total - xp_minimo
    xp_necessario_faixa = xp_proximo - xp_minimo
    xp_faltante = max(
        0,
        xp_proximo - xp_total,
    )

    progresso = (
        xp_atual_faixa
        / xp_necessario_faixa
    )

    return {
        "elo_xp": faixa_atual["elo"],
        "xp_atual_faixa": xp_atual_faixa,
        "xp_necessario_faixa": xp_necessario_faixa,
        "xp_faltante": xp_faltante,
        "progresso": min(1.0, max(0.0, progresso)),
        "nivel_maximo": False,
    }