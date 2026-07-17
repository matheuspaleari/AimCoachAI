from src.load_data import carregar_dados
from src.preprocessing import limpar_dados
from src.save_data import salvar_dados
from src.feature_engineering import criar_features_treino
from src.score_engine import calcular_scores
from src.player_profile import gerar_perfil_jogador
from src.performance_engine import analisar_performance
from src.insights_engine import gerar_insights
from src.utils import log_info, log_aviso


def main():
    # ==========================================================
    # 1. INÍCIO DO PIPELINE
    # ==========================================================

    log_info("Iniciando o pipeline do AimCoachAI.")

    # ==========================================================
    # 2. CARREGA OS DADOS
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

    print("\n")
    print("=" * 45)
    print("👤 PERFIL DO JOGADOR")
    print("=" * 45)
    print(f"🏆 Nível: {perfil['nivel']}")
    print(f"🎯 Estilo: {perfil['estilo']}")
    print(f"⭐ Especialidade: {perfil['especialidade']}")
    print(f"⚠ Ponto de melhoria: {perfil['ponto_fraco']}")
    print(f"📊 Score Geral: {perfil['score_geral']:.2f}")
    print()
    print(f"💬 {perfil['descricao']}")
    print("=" * 45)

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
    # 9. RESUMO
    # ==========================================================

    log_info(f"Registros brutos: {len(dados)}")
    log_info(f"Registros tratados: {len(dados_limpos)}")
    log_info(f"Treinos analisados: {len(features)}")
    log_info("Pipeline finalizado com sucesso.")


if __name__ == "__main__":
    main()