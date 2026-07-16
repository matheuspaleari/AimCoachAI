from src.utils import log_aviso, log_info


NOMES_HABILIDADES = {
    "precisao": "Precisão",
    "velocidade": "Velocidade",
    "controle": "Controle de tiros",
    "consistencia": "Consistência",
}


def classificar_score(score: float) -> str:
    """
    Classifica uma nota de habilidade.
    """

    if score >= 90:
        return "excelente"

    if score >= 80:
        return "muito bom"

    if score >= 70:
        return "bom"

    if score >= 60:
        return "regular"

    return "precisa melhorar"


def interpretar_tendencia(tendencia: str) -> str:
    """
    Transforma a tendência em uma frase curta.
    """

    mensagens = {
        "crescente": "apresenta melhora nos treinos recentes",
        "decrescente": "apresenta queda nos treinos recentes",
        "estável": "permanece estável nos treinos recentes",
        "dados insuficientes": "ainda não possui dados suficientes",
    }

    return mensagens.get(
        tendencia,
        "não foi possível interpretar a tendência",
    )


def criar_insight_habilidade(
    nome: str,
    dados_habilidade: dict,
) -> dict:
    """
    Cria uma análise textual para uma habilidade.
    """

    score = dados_habilidade["score_atual"]
    media = dados_habilidade["media_historica"]
    evolucao = dados_habilidade["variacao_total_percentual"]
    tendencia = dados_habilidade["tendencia_recente"]

    classificacao = classificar_score(score)
    texto_tendencia = interpretar_tendencia(tendencia)

    diferenca_media = round(score - media, 2)

    if diferenca_media > 1:
        comparacao = (
            f"Está {diferenca_media:.2f} pontos acima "
            "da sua média histórica."
        )
    elif diferenca_media < -1:
        comparacao = (
            f"Está {abs(diferenca_media):.2f} pontos abaixo "
            "da sua média histórica."
        )
    else:
        comparacao = "Está próxima da sua média histórica."

    if evolucao > 5:
        texto_evolucao = (
            f"Evoluiu {evolucao:.2f}% desde o primeiro treino."
        )
    elif evolucao < -5:
        texto_evolucao = (
            f"Caiu {abs(evolucao):.2f}% desde o primeiro treino."
        )
    else:
        texto_evolucao = (
            "Apresenta pouca variação desde o primeiro treino."
        )

    mensagem = (
        f"{nome}: desempenho {classificacao}. "
        f"A habilidade {texto_tendencia}. "
        f"{comparacao} {texto_evolucao}"
    )

    return {
        "habilidade": nome,
        "score": score,
        "classificacao": classificacao,
        "tendencia": tendencia,
        "evolucao_percentual": evolucao,
        "mensagem": mensagem,
    }


def gerar_insights(analise: dict) -> dict:
    """
    Gera interpretações a partir da análise de performance.
    """

    if not analise or "resumo" not in analise:
        log_aviso("Nenhuma análise disponível para gerar insights.")
        return {}

    insights_habilidades = {}

    for chave, nome in NOMES_HABILIDADES.items():
        if chave not in analise:
            continue

        insights_habilidades[chave] = criar_insight_habilidade(
            nome,
            analise[chave],
        )

    if not insights_habilidades:
        log_aviso("Nenhuma habilidade disponível para interpretação.")
        return {}

    menor_score = min(
        insights_habilidades,
        key=lambda habilidade: insights_habilidades[habilidade]["score"],
    )

    maior_evolucao = max(
        insights_habilidades,
        key=lambda habilidade: insights_habilidades[habilidade][
            "evolucao_percentual"
        ],
    )

    habilidades_em_queda = [
        insight["habilidade"]
        for insight in insights_habilidades.values()
        if insight["tendencia"] == "decrescente"
    ]

    habilidade_prioritaria = insights_habilidades[menor_score]
    habilidade_destaque = insights_habilidades[maior_evolucao]

    conclusoes = [
        (
            "O principal ponto de melhoria atual é "
            f"{habilidade_prioritaria['habilidade']}, com "
            f"{habilidade_prioritaria['score']:.2f} pontos."
        ),
        (
            "A habilidade com maior evolução foi "
            f"{habilidade_destaque['habilidade']}, com variação de "
            f"{habilidade_destaque['evolucao_percentual']:.2f}%."
        ),
    ]

    if habilidades_em_queda:
        conclusoes.append(
            "As habilidades com tendência de queda são: "
            + ", ".join(habilidades_em_queda)
            + "."
        )
    else:
        conclusoes.append(
            "Nenhuma habilidade apresenta tendência recente de queda."
        )

    resultado = {
        "habilidades": insights_habilidades,
        "principal_ponto_melhoria": habilidade_prioritaria[
            "habilidade"
        ],
        "maior_evolucao": habilidade_destaque["habilidade"],
        "habilidades_em_queda": habilidades_em_queda,
        "conclusoes": conclusoes,
    }

    log_info("Insights do jogador gerados com sucesso.")

    return resultado