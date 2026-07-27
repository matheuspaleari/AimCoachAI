from src.coach_ai import gerar_recomendacao_coach
from src.feature_engineering import criar_features_treino
from src.history_window import obter_janela_historica

from src.load_data import carregar_dados
from src.map_statistics import (
    gerar_estatisticas_mapas,
    salvar_estatisticas_mapas,
)

from src.player_profile import gerar_perfil_jogador
from src.preprocessing import limpar_dados
from src.save_data import salvar_dados
from src.score_engine import calcular_scores
from src.utils import log_aviso, log_info


COLUNAS_SCORE = [
    "score_precisao",
    "score_velocidade",
    "score_controle",
    "score_consistencia",
    "score_geral",
]


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
        log_aviso(
            "Nenhum registro válido permaneceu após a limpeza."
        )
        return

    salvar_dados(dados_limpos)

    # ==========================================================
    # 4. FEATURE ENGINEERING
    # ==========================================================

    features = criar_features_treino(dados_limpos)

    if features.empty:
        log_aviso(
            "Não foi possível criar as features dos treinos."
        )
        return

    features.to_csv(
        "data/processed/features.csv",
        index=False,
        encoding="utf-8-sig",
    )

    log_info(
        "Features salvas em: data/processed/features.csv"
    )

    # ==========================================================
    # 5. JANELA HISTÓRICA
    # ==========================================================

    features_recentes, treino_atual = obter_janela_historica(
        features=features,
        quantidade=30,
    )

    if features_recentes.empty:
        log_aviso(
            "Não foi possível criar a janela histórica."
        )
        return

    if treino_atual.empty:
        log_aviso(
            "Nenhum treino atual foi encontrado."
        )
        return

    # ==========================================================
    # 6. ESTATÍSTICAS DOS MAPAS
    # ==========================================================

    estatisticas_mapas = gerar_estatisticas_mapas(
        features_recentes
    )

    if estatisticas_mapas.empty:
        log_aviso(
            "Não foi possível gerar as estatísticas dos mapas."
        )
        return

    salvar_estatisticas_mapas(
        estatisticas_mapas
    )

    # ==========================================================
    # 7. SCORE ENGINE
    # ==========================================================

    scores = calcular_scores(
        features=treino_atual,
        estatisticas_mapas=estatisticas_mapas,
    )

    if scores.empty:
        log_aviso(
            "Não foi possível calcular os scores."
        )
        return

    # Mantém apenas cenários com histórico suficiente
    if "historico_suficiente" in scores.columns:
        scores_validos = scores[
            scores["historico_suficiente"]
        ].copy()
    else:
        scores_validos = scores.copy()

    scores_validos = scores_validos.dropna(
        subset=COLUNAS_SCORE,
    )

    if scores_validos.empty:
        log_aviso(
            "Nenhum cenário possui histórico suficiente "
            "para gerar perfil e recomendações."
        )
        return

    # ==========================================================
    # 8. PLAYER PROFILE
    # ==========================================================

    perfil = gerar_perfil_jogador(scores_validos)

    if not perfil:
        log_aviso(
            "Não foi possível gerar o perfil do jogador."
        )
        return

    print()
    print("=" * 50)
    print("👤 PERFIL DO JOGADOR")
    print("=" * 50)
    print(f"🏆 Nível: {perfil['nivel']}")
    print(f"🎯 Estilo: {perfil['estilo']}")
    print(f"⭐ Especialidade: {perfil['especialidade']}")
    print(
        f"⚠ Ponto de melhoria: "
        f"{perfil['ponto_fraco']}"
    )
    print(
        f"📊 Score Geral: "
        f"{perfil['score_geral']:.2f}"
    )
    print()
    print(f"💬 {perfil['descricao']}")
    print("=" * 50)

    # ==========================================================
    # ANÁLISE RESUMIDA PARA O COACH AI
    # ==========================================================

    analise_perfil = {
        "resumo": {
            "score_atual": {
                "Precisão": perfil["score_precisao"],
                 "Velocidade": perfil["score_velocidade"],
                "Controle de tiros": perfil["score_controle"],
                 "Consistência": perfil["score_consistencia"],
            }
        },
        "habilidades": {},
    }

    # ==========================================================
    # 11. COACH AI
    # ==========================================================

    recomendacao = gerar_recomendacao_coach(
        scores=scores_validos,
        analise=analise_perfil,
        perfil=perfil,
    )

    if not recomendacao:
        log_aviso(
            "Não foi possível gerar a recomendação do Coach AI."
        )
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
        print(
            f"  Foco: {exercicio['foco']}"
        )

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
    # 12. RESUMO DO PIPELINE
    # ==========================================================

    log_info(
        f"Registros brutos: {len(dados)}"
    )

    log_info(
        f"Registros tratados: {len(dados_limpos)}"
    )

    log_info(
        f"Treinos históricos: {len(features)}"
    )

    log_info(
        f"Treinos usados como referência: "
        f"{len(features_recentes)}"
    )

    log_info(
        f"Treinos atuais avaliados: "
        f"{len(treino_atual)}"
    )

    log_info(
        f"Treinos com histórico suficiente: "
        f"{len(scores_validos)}"
    )

    log_info(
        "Pipeline finalizado com sucesso."
    )


if __name__ == "__main__":
    main()
