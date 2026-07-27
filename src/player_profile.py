import pandas as pd

from src.utils import log_aviso, log_info


HABILIDADES = {
    "score_precisao": "Precisão",
    "score_velocidade": "Velocidade",
    "score_controle": "Controle de tiros",
    "score_consistencia": "Consistência",
}


ESTILOS = {
    "score_precisao": "🎯 Precision Player",
    "score_velocidade": "⚡ Speed Player",
    "score_controle": "🎮 Control Player",
    "score_consistencia": "🧠 Consistent Player",
}


COLUNAS_HABILIDADES = list(HABILIDADES.keys())


def classificar_nivel(score_geral: float) -> str:
    """
    Classifica o elo de mira estimado.

    Não representa o elo competitivo real do VALORANT.
    """

    if pd.isna(score_geral):
        return "Não classificado"

    if score_geral >= 96:
        return "☀️ Radiante"

    if score_geral >= 90:
        return "🔴 Imortal"

    if score_geral >= 83:
        return "🟢 Ascendente"

    if score_geral >= 75:
        return "💎 Diamante"

    if score_geral >= 67:
        return "🔷 Platina"

    if score_geral >= 58:
        return "🟡 Ouro"

    if score_geral >= 45:
        return "⚪ Prata"

    if score_geral >= 25:
        return "🟤 Bronze"

    return "⚙️ Ferro"


def identificar_maior_habilidade(
    scores_medios: pd.Series,
) -> str:
    """
    Retorna a habilidade com maior score médio.
    """

    habilidades_validas = scores_medios[
        COLUNAS_HABILIDADES
    ].dropna()

    if habilidades_validas.empty:
        return "score_precisao"

    return habilidades_validas.idxmax()


def identificar_menor_habilidade(
    scores_medios: pd.Series,
) -> str:
    """
    Retorna a habilidade com menor score médio.
    """

    habilidades_validas = scores_medios[
        COLUNAS_HABILIDADES
    ].dropna()

    if habilidades_validas.empty:
        return "score_precisao"

    return habilidades_validas.idxmin()


def identificar_estilo(
    scores_medios: pd.Series,
) -> str:
    """
    Identifica o estilo predominante considerando
    a média dos cenários avaliados.
    """

    maior_habilidade = identificar_maior_habilidade(
        scores_medios
    )

    return ESTILOS.get(
        maior_habilidade,
        "⚖ Balanced Player",
    )


def gerar_descricao_perfil(
    nivel: str,
    estilo: str,
    especialidade: str,
    ponto_fraco: str,
) -> str:
    """
    Cria uma descrição resumida do perfil atual.
    """

    return (
        f"Jogador de nível {nivel}, com perfil {estilo}. "
        f"Sua principal especialidade é {especialidade}, "
        f"enquanto o ponto prioritário de evolução é "
        f"{ponto_fraco}."
    )


def gerar_perfil_jogador(
    scores: pd.DataFrame,
) -> dict:
    """
    Gera o perfil geral do jogador usando a média dos
    cenários que possuem histórico suficiente.
    """

    if scores.empty:
        log_aviso(
            "Nenhum score disponível para gerar o perfil."
        )
        return {}

    colunas_necessarias = [
        "score_precisao",
        "score_velocidade",
        "score_controle",
        "score_consistencia",
        "score_geral",
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in scores.columns
    ]

    if colunas_ausentes:
        log_aviso(
            "Não foi possível gerar o perfil. "
            f"Colunas ausentes: "
            f"{', '.join(colunas_ausentes)}"
        )
        return {}

    dados_validos = scores.dropna(
        subset=colunas_necessarias,
    ).copy()

    if dados_validos.empty:
        log_aviso(
            "Nenhum score válido disponível para gerar o perfil."
        )
        return {}

    scores_medios = (
        dados_validos[colunas_necessarias]
        .mean()
    )

    maior_habilidade = identificar_maior_habilidade(
        scores_medios
    )

    menor_habilidade = identificar_menor_habilidade(
        scores_medios
    )

    especialidade = HABILIDADES[maior_habilidade]
    ponto_fraco = HABILIDADES[menor_habilidade]

    score_geral = float(
        scores_medios["score_geral"]
    )

    nivel = classificar_nivel(score_geral)
    estilo = identificar_estilo(scores_medios)

    perfil = {
        "treino_atual": "Média dos cenários válidos",
        "cenarios_avaliados": len(dados_validos),
        "nivel": nivel,
        "estilo": estilo,
        "especialidade": especialidade,
        "ponto_fraco": ponto_fraco,
        "score_geral": round(
            score_geral,
            2,
        ),
        "score_precisao": round(
            float(scores_medios["score_precisao"]),
            2,
        ),
        "score_velocidade": round(
            float(scores_medios["score_velocidade"]),
            2,
        ),
        "score_controle": round(
            float(scores_medios["score_controle"]),
            2,
        ),
        "score_consistencia": round(
            float(scores_medios["score_consistencia"]),
            2,
        ),
    }

    perfil["descricao"] = gerar_descricao_perfil(
        nivel=perfil["nivel"],
        estilo=perfil["estilo"],
        especialidade=perfil["especialidade"],
        ponto_fraco=perfil["ponto_fraco"],
    )

    log_info(
        f"Perfil do jogador gerado com base em "
        f"{perfil['cenarios_avaliados']} cenário(s): "
        f"{perfil['nivel']} - {perfil['estilo']}"
    )

    return perfil