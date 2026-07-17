from typing import Any

from src.utils import log_aviso, log_info


PLANOS_TREINO = {
    "Precisão": {
        "objetivo": "Melhorar a precisão dos disparos",
        "exercicios": [
            {
                "nome": "Sixshot",
                "duracao_minutos": 10,
                "foco": "Microajustes e precisão em alvos pequenos",
            },
            {
                "nome": "Microshot",
                "duracao_minutos": 10,
                "foco": "Transições precisas entre alvos próximos",
            },
            {
                "nome": "Precision Grid",
                "duracao_minutos": 5,
                "foco": "Reduzir disparos incorretos",
            },
        ],
    },
    "Velocidade": {
        "objetivo": "Aumentar a velocidade de aquisição de alvos",
        "exercicios": [
            {
                "nome": "Gridshot",
                "duracao_minutos": 10,
                "foco": "Velocidade de troca entre alvos",
            },
            {
                "nome": "Spidershot Speed",
                "duracao_minutos": 10,
                "foco": "Tempo de reação e movimentação rápida",
            },
            {
                "nome": "Microflex",
                "duracao_minutos": 5,
                "foco": "Velocidade com controle",
            },
        ],
    },
    "Controle de tiros": {
        "objetivo": "Reduzir overshots e melhorar o controle dos disparos",
        "exercicios": [
            {
                "nome": "Sixshot",
                "duracao_minutos": 10,
                "foco": "Controle e precisão em alvos pequenos",
            },
            {
                "nome": "Microshot Precision",
                "duracao_minutos": 10,
                "foco": "Parar o movimento antes do disparo",
            },
            {
                "nome": "Gridshot Precision",
                "duracao_minutos": 5,
                "foco": "Reduzir tiros desperdiçados",
            },
        ],
    },
    "Consistência": {
        "objetivo": "Manter um desempenho estável durante toda a sessão",
        "exercicios": [
            {
                "nome": "Gridshot Standard",
                "duracao_minutos": 10,
                "foco": "Manter ritmo constante",
            },
            {
                "nome": "Sixshot",
                "duracao_minutos": 10,
                "foco": "Repetição técnica e estabilidade",
            },
            {
                "nome": "Strafetrack",
                "duracao_minutos": 5,
                "foco": "Controle contínuo durante movimentos",
            },
        ],
    },
}


CHAVES_HABILIDADES = {
    "Precisão": "precisao",
    "Velocidade": "velocidade",
    "Controle de tiros": "controle",
    "Consistência": "consistencia",
}


def classificar_prioridade(
    score: float,
    tendencia: str,
) -> str:
    """
    Classifica a prioridade da recomendação.
    """

    if score < 50:
        return "Crítica"

    if score < 65:
        return "Alta"

    if tendencia == "decrescente":
        return "Alta"

    if score < 80:
        return "Média"

    return "Baixa"


def definir_duracao_total(prioridade: str) -> int:
    """
    Define o tempo total recomendado com base na prioridade.
    """

    duracoes = {
        "Crítica": 35,
        "Alta": 30,
        "Média": 25,
        "Baixa": 20,
    }

    return duracoes.get(prioridade, 25)


def ajustar_duracao_exercicios(
    exercicios: list[dict[str, Any]],
    duracao_total: int,
) -> list[dict[str, Any]]:
    """
    Distribui o tempo total entre os exercícios.
    """

    if not exercicios:
        return []

    quantidade = len(exercicios)
    duracao_base = duracao_total // quantidade
    minutos_restantes = duracao_total % quantidade

    exercicios_ajustados = []

    for indice, exercicio in enumerate(exercicios):
        duracao = duracao_base

        if indice < minutos_restantes:
            duracao += 1

        exercicios_ajustados.append(
            {
                **exercicio,
                "duracao_minutos": duracao,
            }
        )

    return exercicios_ajustados


def gerar_meta(
    habilidade: str,
    score_atual: float,
) -> dict[str, Any]:
    """
    Gera uma meta de curto prazo para a habilidade.
    """

    incremento = 5.0

    if score_atual < 50:
        incremento = 8.0
    elif score_atual >= 80:
        incremento = 3.0

    score_meta = min(100.0, score_atual + incremento)

    return {
        "habilidade": habilidade,
        "score_atual": round(score_atual, 2),
        "score_meta": round(score_meta, 2),
        "ganho_necessario": round(score_meta - score_atual, 2),
    }


def gerar_explicacao(
    habilidade: str,
    score_atual: float,
    media_historica: float,
    tendencia: str,
    evolucao_percentual: float,
) -> str:
    """
    Explica por que a habilidade foi escolhida como prioridade.
    """

    partes = [
        (
            f"{habilidade} foi selecionada como foco principal "
            f"porque possui score atual de {score_atual:.2f} pontos."
        )
    ]

    diferenca_media = score_atual - media_historica

    if diferenca_media > 2:
        partes.append(
            f"O resultado atual está {diferenca_media:.2f} pontos "
            "acima da média histórica."
        )
    elif diferenca_media < -2:
        partes.append(
            f"O resultado atual está {abs(diferenca_media):.2f} pontos "
            "abaixo da média histórica."
        )
    else:
        partes.append(
            "O resultado atual está próximo da média histórica."
        )

    if tendencia == "crescente":
        partes.append(
            "A tendência recente é positiva, então o objetivo é "
            "manter o ritmo de evolução."
        )
    elif tendencia == "decrescente":
        partes.append(
            "A tendência recente é de queda, por isso essa habilidade "
            "deve receber atenção imediata."
        )
    elif tendencia == "estável":
        partes.append(
            "A habilidade está estável nos treinos recentes e precisa "
            "de estímulos diferentes para voltar a evoluir."
        )
    else:
        partes.append(
            "Ainda não existem dados recentes suficientes para avaliar "
            "a tendência com segurança."
        )

    if evolucao_percentual > 10:
        partes.append(
            f"Desde o primeiro treino, houve evolução de "
            f"{evolucao_percentual:.2f}%."
        )
    elif evolucao_percentual < -5:
        partes.append(
            f"Desde o primeiro treino, houve queda de "
            f"{abs(evolucao_percentual):.2f}%."
        )

    return " ".join(partes)


def identificar_habilidade_prioritaria(
    analise: dict,
) -> tuple[str, dict]:
    """
    Define a habilidade que deve receber maior atenção.

    A prioridade considera score atual e tendência recente.
    """

    candidatos = []

    for nome_habilidade, chave_analise in CHAVES_HABILIDADES.items():
        dados_habilidade = analise.get(chave_analise, {})

        score = float(
            dados_habilidade.get("score_atual", 100)
        )

        tendencia = dados_habilidade.get(
            "tendencia_recente",
            "dados insuficientes",
        )

        penalidade_tendencia = {
            "decrescente": 12,
            "estável": 4,
            "crescente": 0,
            "dados insuficientes": 2,
        }.get(tendencia, 0)

        score_prioridade = score - penalidade_tendencia

        candidatos.append(
            {
                "habilidade": nome_habilidade,
                "dados": dados_habilidade,
                "score_prioridade": score_prioridade,
            }
        )

    habilidade_prioritaria = min(
        candidatos,
        key=lambda item: item["score_prioridade"],
    )

    return (
        habilidade_prioritaria["habilidade"],
        habilidade_prioritaria["dados"],
    )


def gerar_recomendacao_coach(
    scores,
    analise,
    perfil,
):
    """
    Gera um plano personalizado de treino para o jogador.
    """

    if scores.empty:
        log_aviso(
            "Nenhum score disponível para gerar recomendação."
        )
        return {}

    if not analise:
        log_aviso(
            "Nenhuma análise disponível para gerar recomendação."
        )
        return {}

    if not perfil:
        log_aviso(
            "Nenhum perfil disponível para gerar recomendação."
        )
        return {}

    habilidade, dados_habilidade = (
        identificar_habilidade_prioritaria(analise)
    )

    plano_base = PLANOS_TREINO.get(habilidade)

    if not plano_base:
        log_aviso(
            f"Nenhum plano encontrado para a habilidade: {habilidade}."
        )
        return {}

    score_atual = float(
        dados_habilidade.get("score_atual", 0)
    )

    media_historica = float(
        dados_habilidade.get("media_historica", 0)
    )

    tendencia = dados_habilidade.get(
        "tendencia_recente",
        "dados insuficientes",
    )

    evolucao_percentual = float(
        dados_habilidade.get(
            "variacao_total_percentual",
            0,
        )
    )

    prioridade = classificar_prioridade(
        score=score_atual,
        tendencia=tendencia,
    )

    duracao_total = definir_duracao_total(prioridade)

    exercicios = ajustar_duracao_exercicios(
        exercicios=plano_base["exercicios"],
        duracao_total=duracao_total,
    )

    meta = gerar_meta(
        habilidade=habilidade,
        score_atual=score_atual,
    )

    explicacao = gerar_explicacao(
        habilidade=habilidade,
        score_atual=score_atual,
        media_historica=media_historica,
        tendencia=tendencia,
        evolucao_percentual=evolucao_percentual,
    )

    recomendacao = {
        "treino_atual": scores.iloc[-1]["Treino"],
        "nivel_jogador": perfil["nivel"],
        "estilo_jogador": perfil["estilo"],
        "habilidade_prioritaria": habilidade,
        "objetivo_principal": plano_base["objetivo"],
        "prioridade": prioridade,
        "duracao_total_minutos": duracao_total,
        "tendencia": tendencia,
        "exercicios": exercicios,
        "meta": meta,
        "explicacao": explicacao,
    }

    log_info(
        "Recomendação do Coach AI gerada para "
        f"{habilidade} com prioridade {prioridade}."
    )

    return recomendacao