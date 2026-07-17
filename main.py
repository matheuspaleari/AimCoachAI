from src.coach_ai import gerar_recomendacao_coach
from src.feature_engineering import criar_features_treino
from src.insights_engine import gerar_insights
from src.load_data import carregar_dados
from src.performance_engine import analisar_performance
from src.player_profile import gerar_perfil_jogador
from src.preprocessing import limpar_dados
from src.save_data import salvar_dados
from src.score_engine import calcular_scores
from src.utils import log_aviso, log_info


def main():
    # ==========================================================
    # 1. INÍCIO DO PIPELINE
    # ==========================================================

    log_info("Iniciando o pipeline do AimCoachAI.")

    # ==========================================================
    # 2. CARREGAMENTO DOS DADOS
    # ==========================================================

    dados = carregar_dados()

    if dados.empty:
        log_aviso("Adicione arquivos CSV em data/raw.")
        return

    # ==========================================================
    # 3. PRÉ-PROCESSAMENTO
    # ==========================================================

    dados_limpos = limpar_dados(dados)

    if dados_limpos.empty:
        log_aviso("Nenhum registro válido permaneceu após a limpeza.")
        return

    salvar_dados(dados_limpos)

    # ==========================================================
    # 4. FEATURE ENGINEERING
    # ==========================================================

    features = criar_features_treino(dados_limpos)

    if features.empty:
        log_aviso("Não foi possível criar as features dos treinos.")
        return

    # ==========================================================
    # 5. SCORE ENGINE
    # ==========================================================

    scores = calcular_scores(features)

    if scores.empty:
        log_aviso("Não foi possível calcular os scores.")
        return

    # ==========================================================
    # 6. PLAYER PROFILE ENGINE
    # ==========================================================

    perfil = gerar_perfil_jogador(scores)

    if not perfil:
        log_aviso("Não foi possível gerar o perfil do jogador.")
        return

    print()
    print("=" * 50)
    print("👤 PERFIL DO JOGADOR")
    print("=" * 50)
    print(f"🏆 Nível: {perfil['nivel']}")
    print(f"🎯 Estilo: {perfil['estilo']}")
    print(f"⭐ Especialidade: {perfil['especialidade']}")
    print(f"⚠ Ponto de melhoria: {perfil['ponto_fraco']}")
    print(f"📊 Score Geral: {perfil['score_geral']:.2f}")
    print()
    print(f"💬 {perfil['descricao']}")
    print("=" * 50)

    # ==========================================================
    # 7. PERFORMANCE ENGINE
    # ==========================================================

    analise = analisar_performance(scores)

    if not analise:
        log_aviso("Não foi possível analisar a evolução.")
        return

    # ==========================================================
    # 8. INSIGHTS ENGINE
    # ==========================================================

    insights = gerar_insights(analise)

    if not insights:
        log_aviso("Não foi possível gerar os insights.")
        return

    print("\n📈 Análise por habilidade:\n")

    for insight in insights["habilidades"].values():
        print(f"- {insight['mensagem']}")

    print("\nConclusão:")

    for linha in insights["conclusoes"]:
        print(f"- {linha}")

    # ==========================================================
    # 9. COACH AI
    # ==========================================================

    recomendacao = gerar_recomendacao_coach(
        scores=scores,
        analise=analise,
        perfil=perfil,
    )

    if not recomendacao:
        log_aviso("Não foi possível gerar a recomendação do Coach AI.")
        return

    print()
    print("=" * 50)
    print("🧠 COACH AI")
    print("=" * 50)

    print(
        f"🎯 Habilidade prioritária: "
        f"{recomendacao['habilidade_prioritaria']}"
    )

    print(
        f"📌 Objetivo principal: "
        f"{recomendacao['objetivo_principal']}"
    )

    print(
        f"⚠ Prioridade: "
        f"{recomendacao['prioridade']}"
    )

    print(
        f"📈 Tendência atual: "
        f"{recomendacao['tendencia']}"
    )

    print(
        f"⏱ Tempo total sugerido: "
        f"{recomendacao['duracao_total_minutos']} minutos"
    )

    print("\n📋 Plano recomendado:")

    for exercicio in recomendacao["exercicios"]:
        print(
            f"- {exercicio['nome']}: "
            f"{exercicio['duracao_minutos']} minutos"
        )
        print(f"  Foco: {exercicio['foco']}")

    meta = recomendacao["meta"]

    print("\n🏁 Meta de curto prazo:")
    print(
        f"{meta['habilidade']}: "
        f"{meta['score_atual']:.2f} → "
        f"{meta['score_meta']:.2f} pontos"
    )

    print(
        f"Ganho necessário: "
        f"{meta['ganho_necessario']:.2f} pontos"
    )

    print("\n💬 Motivo da recomendação:")
    print(recomendacao["explicacao"])

    print("=" * 50)

    # ==========================================================
    # 10. RESUMO DO PIPELINE
    # ==========================================================

    log_info(f"Registros brutos: {len(dados)}")
    log_info(f"Registros tratados: {len(dados_limpos)}")
    log_info(f"Treinos analisados: {len(features)}")
    log_info("Pipeline finalizado com sucesso.")


if __name__ == "__main__":
    main()