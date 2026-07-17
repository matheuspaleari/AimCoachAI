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


def classificar_nivel(score_geral: float) -> str:
    """
    Classifica o nível atual do jogador com base no score geral.
    """

    if pd.isna(score_geral):
        return "Não classificado"

    if score_geral >= 85:
        return "Elite"

    if score_geral >= 70:
        return "Avançado"

    if score_geral >= 50:
        return "Intermediário"

    return "Iniciante"


def identificar_maior_habilidade(treino: pd.Series) -> str:
    """
    Retorna o nome técnico da habilidade com maior score.
    """

    scores_habilidades = {
        coluna: treino.get(coluna, 0)
        for coluna in HABILIDADES
    }

    return max(
        scores_habilidades,
        key=scores_habilidades.get,
    )


def identificar_menor_habilidade(treino: pd.Series) -> str:
    """
    Retorna o nome técnico da habilidade com menor score.
    """

    scores_habilidades = {
        coluna: treino.get(coluna, 0)
        for coluna in HABILIDADES
    }

    return min(
        scores_habilidades,
        key=scores_habilidades.get,
    )


def identificar_estilo(treino: pd.Series) -> str:
    """
    Identifica o estilo predominante do jogador.
    """

    maior_habilidade = identificar_maior_habilidade(treino)

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
        f"enquanto o ponto prioritário de evolução é {ponto_fraco}."
    )


def gerar_perfil_jogador(scores: pd.DataFrame) -> dict:
    """
    Gera o perfil do jogador com base no treino mais recente.

    Retorna nível, estilo, especialidade, ponto fraco
    e os scores atuais.
    """

    if scores.empty:
        log_aviso("Nenhum score disponível para gerar o perfil.")
        return {}

    colunas_necessarias = [
        "Treino",
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
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return {}

    treino_atual = scores.iloc[-1]

    maior_habilidade = identificar_maior_habilidade(treino_atual)
    menor_habilidade = identificar_menor_habilidade(treino_atual)

    especialidade = HABILIDADES[maior_habilidade]
    ponto_fraco = HABILIDADES[menor_habilidade]

    score_geral = float(treino_atual["score_geral"])
    nivel = classificar_nivel(score_geral)
    estilo = identificar_estilo(treino_atual)

    perfil = {
        "treino_atual": treino_atual["Treino"],
        "nivel": nivel,
        "estilo": estilo,
        "especialidade": especialidade,
        "ponto_fraco": ponto_fraco,
        "score_geral": round(score_geral, 2),
        "score_precisao": round(
            float(treino_atual["score_precisao"]),
            2,
        ),
        "score_velocidade": round(
            float(treino_atual["score_velocidade"]),
            2,
        ),
        "score_controle": round(
            float(treino_atual["score_controle"]),
            2,
        ),
        "score_consistencia": round(
            float(treino_atual["score_consistencia"]),
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
        f"Perfil do jogador gerado: "
        f"{perfil['nivel']} - {perfil['estilo']}"
    )

    return perfil