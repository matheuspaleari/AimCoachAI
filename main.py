from src.feature_engineering import criar_features_treino
from src.insights_engine import gerar_insights
from src.load_data import carregar_dados
from src.performance_engine import analisar_performance
from src.preprocessing import limpar_dados
from src.save_data import salvar_dados
from src.score_engine import calcular_scores
from src.utils import log_aviso, log_info


def main():
    log_info("Iniciando o pipeline do AimCoachAI.")

    # 1. Carrega os arquivos CSV
    dados = carregar_dados()

    if dados.empty:
        log_aviso("Adicione arquivos CSV em data/raw.")
        return

    # 2. Limpa e padroniza os dados
    dados_limpos = limpar_dados(dados)

    if dados_limpos.empty:
        log_aviso("Nenhum registro válido permaneceu após a limpeza.")
        return

    # 3. Salva o histórico tratado
    salvar_dados(dados_limpos)

    # 4. Cria as features por treino
    features = criar_features_treino(dados_limpos)

    if features.empty:
        log_aviso("Não foi possível criar as features dos treinos.")
        return

    # 5. Calcula os scores
    scores = calcular_scores(features)

    if scores.empty:
        log_aviso("Não foi possível calcular os scores.")
        return

    colunas_scores = [
        "Treino",
        "score_precisao",
        "score_velocidade",
        "score_controle",
        "score_consistencia",
        "score_geral",
    ]

    print("\nScores calculados:")
    print(scores[colunas_scores].to_string(index=False))

    # 6. Analisa a evolução do jogador
    analise = analisar_performance(scores)

    if not analise:
        log_aviso("Não foi possível analisar a evolução do jogador.")
        return

    resumo = analise["resumo"]

    print("\nResultado do treino mais recente:")
    print(f"Treino: {resumo['treino_atual']}")
    print(f"Score geral: {analise['geral']['score_atual']:.2f}")
    print(
        "Principal ponto de melhoria: "
        f"{resumo['principal_ponto_atual']}"
    )

    print("\nAnálise de evolução:")
    print(
        f"Melhor treino: {resumo['melhor_treino']} "
        f"({resumo['melhor_score_geral']:.2f} pontos)"
    )
    print(
        f"Pior treino: {resumo['pior_treino']} "
        f"({resumo['pior_score_geral']:.2f} pontos)"
    )

    nomes_habilidades = {
        "precisao": "Precisão",
        "velocidade": "Velocidade",
        "controle": "Controle de tiros",
        "consistencia": "Consistência",
    }

    print("\nEvolução por habilidade:")

    for chave, nome in nomes_habilidades.items():
        resultado = analise[chave]

        print(
            f"{nome}: "
            f"{resultado['score_atual']:.2f} pontos | "
            f"Média histórica: {resultado['media_historica']:.2f} | "
            f"Tendência recente: {resultado['tendencia_recente']} | "
            f"Evolução total: "
            f"{resultado['variacao_total_percentual']:.2f}%"
        )

    if resumo["habilidades_em_queda"]:
        print(
            "\nHabilidades em queda: "
            + ", ".join(resumo["habilidades_em_queda"])
        )
    else:
        print("\nNenhuma habilidade apresenta tendência de queda.")

    # 7. Gera os insights em linguagem natural
    insights = gerar_insights(analise)

    if not insights:
        log_aviso("Não foi possível gerar os insights do jogador.")
        return

    print("\nInsights do jogador:")

    for insight in insights["habilidades"].values():
        print(f"\n- {insight['mensagem']}")

    print("\nConclusão:")

    for conclusao in insights["conclusoes"]:
        print(f"- {conclusao}")

    # 8. Resumo técnico do pipeline
    log_info(f"Registros brutos: {len(dados)}")
    log_info(f"Registros tratados: {len(dados_limpos)}")
    log_info(f"Treinos analisados: {len(scores)}")
    log_info("Pipeline finalizado com sucesso.")


if __name__ == "__main__":
    main()