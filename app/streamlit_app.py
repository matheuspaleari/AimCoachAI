import sys
from pathlib import Path
import pandas as pd

import plotly.graph_objects as go
import streamlit as st


# ==========================================================
# CONFIGURAÇÃO DE IMPORTAÇÃO
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.coach_ai import gerar_recomendacao_coach
from src.feature_engineering import criar_features_treino
from src.history_window import obter_janela_historica
from src.load_data import carregar_dados
from src.map_statistics import gerar_estatisticas_mapas
from src.performance_engine import (
    analisar_performance_cenario,
)
from src.player_profile import gerar_perfil_jogador
from src.preprocessing import limpar_dados
from src.score_engine import calcular_scores
from src.xp_engine import (
    calcular_xp_jogador,
    obter_progresso_xp,
)



# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="AimCoachAI",
    page_icon="🎯",
    layout="wide",
)


# ==========================================================
# PIPELINE
# ==========================================================

def executar_pipeline():
    """
    Executa o pipeline do dashboard.

    Retorna:
    - scores_historicos: todos os treinos usados nos gráficos;
    - scores_atuais: último treino válido de cada cenário;
    - perfil: perfil geral calculado com os cenários válidos;
    - recomendacao: plano criado pelo Coach AI;
    - xp: progresso acumulado do jogador.
    """

    # ==========================================================
    # 1. CARREGAMENTO
    # ==========================================================

    dados = carregar_dados()

    if dados.empty:
        return None, None, None, None, None

    # ==========================================================
    # 2. PRÉ-PROCESSAMENTO
    # ==========================================================

    dados_limpos = limpar_dados(dados)

    if dados_limpos.empty:
        return None, None, None, None, None

    # ==========================================================
    # 3. FEATURE ENGINEERING
    # ==========================================================

    features = criar_features_treino(
        dados_limpos
    )

    if features.empty:
        return None, None, None, None, None

    # ==========================================================
    # 4. JANELA HISTÓRICA
    # ==========================================================

    features_recentes, treino_atual = (
        obter_janela_historica(
            features=features,
            quantidade=30,
        )
    )

    if features_recentes.empty:
        return None, None, None, None, None

    if treino_atual.empty:
        return None, None, None, None, None

    # ==========================================================
    # 5. ESTATÍSTICAS POR CENÁRIO
    # ==========================================================

    estatisticas_mapas = gerar_estatisticas_mapas(
        features_recentes
    )

    if estatisticas_mapas.empty:
        return None, None, None, None, None

    # ==========================================================
    # 6. SCORES HISTÓRICOS PARA GRÁFICOS E XP
    # ==========================================================

    scores_historicos = calcular_scores(
        features=features,
        estatisticas_mapas=estatisticas_mapas,
    )

    if scores_historicos.empty:
        return None, None, None, None, None

    # ==========================================================
    # 7. XP DO JOGADOR
    # ==========================================================

    xp_jogador = calcular_xp_jogador(
        scores_historicos
    )

    if not xp_jogador:
        return None, None, None, None, None

    progresso_xp = obter_progresso_xp(
        xp_jogador["xp_total"]
    )

    xp = {
        **xp_jogador,
        **progresso_xp,
    }

    # ==========================================================
    # 8. SCORES ATUAIS PARA PERFIL E COACH AI
    # ==========================================================

    scores_atuais = calcular_scores(
        features=treino_atual,
        estatisticas_mapas=estatisticas_mapas,
    )

    if scores_atuais.empty:
        return None, None, None, None, None

    if "historico_suficiente" in scores_atuais.columns:
        scores_atuais = scores_atuais[
            scores_atuais["historico_suficiente"]
        ].copy()

    colunas_score = [
        "score_precisao",
        "score_velocidade",
        "score_controle",
        "score_consistencia",
        "score_geral",
    ]

    scores_atuais = scores_atuais.dropna(
        subset=colunas_score
    )

    if scores_atuais.empty:
        return None, None, None, None, None

    # ==========================================================
    # 9. PERFIL GERAL
    # ==========================================================

    perfil = gerar_perfil_jogador(
        scores_atuais
    )

    if not perfil:
        return None, None, None, None, None

    # ==========================================================
    # 10. RESUMO PARA O COACH AI
    # ==========================================================

    analise_perfil = {
        "resumo": {
            "score_atual": {
                "Precisão": perfil["score_precisao"],
                "Velocidade": perfil["score_velocidade"],
                "Controle de tiros": perfil["score_controle"],
                "Consistência": perfil["score_consistencia"],
            },
            "principal_ponto_atual": perfil["ponto_fraco"],
        },
        "habilidades": {},
    }

    # ==========================================================
    # 11. COACH AI
    # ==========================================================

    recomendacao = gerar_recomendacao_coach(
        scores=scores_atuais,
        analise=analise_perfil,
        perfil=perfil,
    )

    if not recomendacao:
        return None, None, None, None, None

    return (
        scores_historicos,
        scores_atuais,
        perfil,
        recomendacao,
        xp,
    )

def formatar_numero(valor: int | float) -> str:
    """
    Formata números usando ponto como separador de milhar.
    """

    return f"{valor:,.0f}".replace(",", ".")


def renderizar_cabecalho_premium(
    perfil: dict,
    xp: dict,
) -> None:
    """
    Renderiza um cabeçalho premium usando apenas
    componentes nativos do Streamlit.
    """

    progresso = float(
        xp.get("progresso", 0.0)
    )

    progresso = max(
        0.0,
        min(1.0, progresso),
    )

    elo_mira = perfil.get(
        "nivel",
        "Não classificado",
    )

    elo_experiencia = xp.get(
        "elo_xp",
        "Não classificado",
    )

    estilo = perfil.get(
        "estilo",
        "⚖ Balanced Player",
    )

    xp_total = int(
        xp.get("xp_total", 0)
    )

    xp_atual_faixa = int(
        xp.get("xp_atual_faixa", 0)
    )

    xp_necessario_faixa = int(
        xp.get("xp_necessario_faixa", 0)
    )

    xp_faltante = int(
        xp.get("xp_faltante", 0)
    )

    quantidade_treinos = int(
        xp.get("quantidade_treinos", 0)
    )

    nivel_maximo = bool(
        xp.get("nivel_maximo", False)
    )

    with st.container(border=True):
        coluna_titulo, coluna_elo = st.columns(
            [3, 1]
        )

        with coluna_titulo:
            st.title("🎯 AimCoachAI")
            st.caption(
                "Perfil competitivo, progressão e evolução "
                "nos treinos de mira."
            )

        with coluna_elo:
            st.metric(
                "Elo de mira estimado",
                elo_mira,
            )

        st.divider()

        coluna1, coluna2, coluna3, coluna4 = st.columns(4)

        coluna1.metric(
            "Elo de experiência",
            elo_experiencia,
        )

        coluna2.metric(
            "Estilo",
            estilo,
        )

        coluna3.metric(
            "XP total",
            formatar_numero(xp_total),
        )

        coluna4.metric(
            "Treinos contabilizados",
            quantidade_treinos,
        )

        st.write("**Progresso de experiência**")

        if nivel_maximo:
            st.progress(
                1.0,
                text="🌟 Nível máximo de experiência alcançado",
            )

            st.success(
                "Você alcançou o maior elo de experiência."
            )
        else:
            texto_progresso = (
                f"{formatar_numero(xp_atual_faixa)} / "
                f"{formatar_numero(xp_necessario_faixa)} XP"
            )

            st.progress(
                progresso,
                text=texto_progresso,
            )

            st.caption(
                f"Faltam {formatar_numero(xp_faltante)} XP "
                f"para o próximo elo de experiência."
            )


def filtrar_periodo(
    scores,
    periodo_selecionado: str,
):
    """
    Filtra o histórico de scores conforme o período selecionado.
    """

    periodos = {
        "Últimos 10 treinos": 10,
        "Últimos 30 treinos": 30,
        "Últimos 50 treinos": 50,
        "Últimos 100 treinos": 100,
    }

    if periodo_selecionado == "Todo o histórico":
        return scores.copy()

    quantidade = periodos[periodo_selecionado]

    return scores.tail(quantidade).copy()



# ==========================================================
# EXECUÇÃO DO PIPELINE
# ==========================================================

scores, scores_atuais, perfil, recomendacao, xp = (
    executar_pipeline()
)


if scores is None:
    st.warning(
        "Não foi possível carregar os dados ou gerar as análises. "
        "Confira se existem arquivos CSV em data/raw."
    )
    st.stop()

renderizar_cabecalho_premium(
    perfil=perfil,
    xp=xp,
)

treino_atual = scores_atuais.iloc[-1]



# ==========================================================
# PERFIL DO JOGADOR
# ==========================================================

st.subheader("👤 Perfil do jogador")

col_perfil1, col_perfil2, col_perfil3, col_perfil4 = st.columns(4)

col_perfil1.metric(
    "Nível",
    perfil["nivel"],
)

col_perfil2.metric(
    "Estilo",
    perfil["estilo"],
)

col_perfil3.metric(
    "Especialidade",
    perfil["especialidade"],
)

col_perfil4.metric(
    "Ponto de melhoria",
    perfil["ponto_fraco"],
)

st.info(perfil["descricao"])

st.divider()


# ==========================================================
# RESUMO DO TREINO ATUAL
# ==========================================================

st.subheader("📊 Resumo do treino atual")

coluna1, coluna2, coluna3, coluna4, coluna5 = st.columns(5)

coluna1.metric(
    "⭐ Score geral",
    f"{treino_atual['score_geral']:.2f}",
)

coluna2.metric(
    "🎯 Precisão",
    f"{treino_atual['score_precisao']:.2f}",
)

coluna3.metric(
    "⚡ Velocidade",
    f"{treino_atual['score_velocidade']:.2f}",
)

coluna4.metric(
    "🔫 Controle",
    f"{treino_atual['score_controle']:.2f}",
)

coluna5.metric(
    "📊 Consistência",
    f"{treino_atual['score_consistencia']:.2f}",
)

st.divider()


# ==========================================================
# PRINCIPAL PONTO DE MELHORIA
# ==========================================================

st.subheader("🎯 Principal ponto de melhoria")

st.error(
    f"A habilidade que mais precisa de atenção é {perfil['ponto_fraco']}."
)

st.divider()

# ==========================================================
# EVOLUÇÃO POR CATEGORIA
# ==========================================================

st.subheader("📈 Evolução por categoria")


def criar_grafico_categoria(
    dados_categoria,
    categoria: str,
):
    """
    Cria o gráfico de evolução de uma categoria específica.

    Quando um mapa é selecionado, também exibe a análise
    de evolução daquele cenário ao longo do tempo.
    """

    if dados_categoria.empty:
        st.warning(
            f"Nenhum treino encontrado para a categoria {categoria}."
        )
        return

    # ==========================================================
    # MAPAS DISPONÍVEIS
    # ==========================================================

    mapas_disponiveis = sorted(
        dados_categoria["Cenario"]
        .dropna()
        .unique()
        .tolist()
    )

    col_mapa, col_periodo, col_quantidade = st.columns(
        [2, 1.3, 1]
    )

    with col_mapa:
        mapa_selecionado = st.selectbox(
            "Mapa analisado",
            options=["Todos os mapas"] + mapas_disponiveis,
            key=f"mapa_{categoria}",
        )

    # Mantém uma cópia da categoria antes dos filtros
    dados_categoria_filtrados = dados_categoria.copy()

    if mapa_selecionado != "Todos os mapas":
        dados_categoria_filtrados = (
            dados_categoria_filtrados[
                dados_categoria_filtrados["Cenario"]
                == mapa_selecionado
            ]
            .copy()
        )

    # ==========================================================
    # FILTRO DE PERÍODO
    # ==========================================================

    with col_periodo:
        periodo_selecionado = st.selectbox(
            "Período",
            options=[
                "Últimos 10 treinos",
                "Últimos 30 treinos",
                "Últimos 50 treinos",
                "Últimos 100 treinos",
                "Todo o histórico",
            ],
            index=3,
            key=f"periodo_{categoria}",
        )

    dados_filtrados = filtrar_periodo(
        scores=dados_categoria_filtrados,
        periodo_selecionado=periodo_selecionado,
    )

    with col_quantidade:
        st.metric(
            "Treinos exibidos",
            len(dados_filtrados),
        )

    if dados_filtrados.empty:
        st.warning(
            "Nenhum treino disponível para os filtros selecionados."
        )
        return

    # ==========================================================
    # ANÁLISE DO CENÁRIO SELECIONADO
    # ==========================================================

    if mapa_selecionado != "Todos os mapas":
        analise_cenario = analisar_performance_cenario(
            scores=dados_categoria_filtrados,
            cenario=mapa_selecionado,
        )

        if analise_cenario:
            st.write("**📊 Resumo da evolução do cenário**")

            col_evolucao1, col_evolucao2, col_evolucao3, col_evolucao4 = (
                st.columns(4)
            )

            colunas_evolucao = [
                col_evolucao1,
                col_evolucao2,
                col_evolucao3,
                col_evolucao4,
            ]

            habilidades_exibidas = [
                "score_precisao",
                "score_velocidade",
                "score_controle",
                "score_consistencia",
            ]

            for coluna_ui, habilidade in zip(
                colunas_evolucao,
                habilidades_exibidas,
            ):
                dados_habilidade = analise_cenario[
                    "habilidades"
                ].get(habilidade)

                if not dados_habilidade:
                    coluna_ui.metric(
                        habilidade.replace(
                            "score_",
                            "",
                        ).capitalize(),
                        "N/A",
                    )
                    continue

                coluna_ui.metric(
                    dados_habilidade["nome"],
                    f"{dados_habilidade['media_recente']:.2f}",
                    delta=(
                        f"{dados_habilidade['variacao_pontos']:+.2f} pts"
                    ),
                )

            st.caption(
                f"Comparação entre os primeiros e os últimos "
                f"{analise_cenario['janela_comparacao']} treino(s) "
                f"do cenário selecionado."
            )

    # ==========================================================
    # PREPARAÇÃO DO HISTÓRICO
    # ==========================================================

    colunas_score = [
        "score_precisao",
        "score_velocidade",
        "score_controle",
        "score_consistencia",
        "score_geral",
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_score
        if coluna not in dados_filtrados.columns
    ]

    if colunas_ausentes:
        st.error(
            "Não foi possível gerar o gráfico. "
            f"Colunas ausentes: {', '.join(colunas_ausentes)}"
        )
        return

    historico = (
        dados_filtrados
        .set_index("Treino")[colunas_score]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
    )

    # Remove somente linhas em que todos os scores são ausentes
    historico = historico.dropna(
        how="all",
        subset=colunas_score,
    )

    if historico.empty:
        st.warning(
            "Não há histórico suficiente para gerar este gráfico. "
            "São necessários pelo menos 5 treinos anteriores "
            "no mesmo cenário."
        )
        return

    # Mantém apenas colunas que possuem pelo menos um valor válido
    colunas_validas = [
        coluna
        for coluna in colunas_score
        if historico[coluna].notna().any()
    ]

    if not colunas_validas:
        st.warning(
            "Nenhuma habilidade possui scores válidos "
            "para os filtros selecionados."
        )
        return

    historico = historico[colunas_validas]

    historico_ema = historico.ewm(
        span=min(
            20,
            max(2, len(historico)),
        ),
        adjust=False,
    ).mean()

    melhores = {
        coluna: historico[coluna].idxmax()
        for coluna in colunas_validas
        if historico[coluna].notna().any()
    }

    # ==========================================================
    # CRIAÇÃO DO GRÁFICO
    # ==========================================================

    fig_categoria = go.Figure()

    def adicionar_habilidade_categoria(
        coluna: str,
        nome: str,
        largura_tendencia: int = 4,
        tamanho_melhor: int = 12,
    ):
        """
        Adiciona o resultado real, a tendência EMA
        e o melhor resultado da habilidade.
        """

        if coluna not in melhores:
            return

        serie_valida = historico[coluna].dropna()

        if serie_valida.empty:
            return

        melhor_treino = melhores[coluna]
        melhor_valor = serie_valida.loc[
            melhor_treino
        ]

        # Linha real
        fig_categoria.add_trace(
            go.Scatter(
                x=historico.index,
                y=historico[coluna],
                mode="lines",
                name=nome,
                opacity=0.18,
                line=dict(width=1),
                connectgaps=False,
                hovertemplate=(
                    f"{nome}: %{{y:.2f}}"
                    "<extra></extra>"
                ),
            )
        )

        # Linha de tendência
        fig_categoria.add_trace(
            go.Scatter(
                x=historico_ema.index,
                y=historico_ema[coluna],
                mode="lines",
                showlegend=False,
                line=dict(
                    width=largura_tendencia,
                ),
                connectgaps=False,
                hoverinfo="skip",
            )
        )

        # Melhor resultado
        fig_categoria.add_trace(
            go.Scatter(
                x=[melhor_treino],
                y=[melhor_valor],
                mode="markers",
                showlegend=False,
                marker=dict(
                    symbol="diamond",
                    size=tamanho_melhor,
                    line=dict(width=1),
                ),
                hovertemplate=(
                    f"🏆 Melhor {nome}<br>"
                    "Treino: %{x}<br>"
                    "Score: %{y:.2f}"
                    "<extra></extra>"
                ),
            )
        )

    adicionar_habilidade_categoria(
        coluna="score_precisao",
        nome="🎯 Precisão",
    )

    adicionar_habilidade_categoria(
        coluna="score_velocidade",
        nome="⚡ Velocidade",
    )

    adicionar_habilidade_categoria(
        coluna="score_controle",
        nome="🔫 Controle",
    )

    adicionar_habilidade_categoria(
        coluna="score_consistencia",
        nome="📊 Consistência",
    )

    adicionar_habilidade_categoria(
        coluna="score_geral",
        nome="⭐ Score Geral",
        largura_tendencia=6,
        tamanho_melhor=15,
    )

    if not fig_categoria.data:
        st.warning(
            "Não existem scores válidos suficientes "
            "para construir o gráfico."
        )
        return

    titulo_mapa = (
        mapa_selecionado
        if mapa_selecionado != "Todos os mapas"
        else categoria
    )

    fig_categoria.update_layout(
        title=(
            f"Evolução — {titulo_mapa} — "
            f"{periodo_selecionado}"
        ),
        xaxis_title="Treinos",
        yaxis_title="Score",
        yaxis=dict(
            range=[0, 100],
        ),
        xaxis=dict(
            rangeslider=dict(
                visible=len(historico) > 30,
                thickness=0.06,
            ),
        ),
        hovermode="x unified",
        template="plotly_dark",
        height=650,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=13),
        ),
        margin=dict(
            l=50,
            r=30,
            t=100,
            b=60,
        ),
    )

    st.plotly_chart(
        fig_categoria,
        width="stretch",
        key=(
            f"grafico_{categoria}_"
            f"{mapa_selecionado}_"
            f"{periodo_selecionado}"
        ),
    )

    st.caption(
        "As linhas transparentes representam os resultados reais. "
        "As linhas fortes representam a tendência EMA. "
        "Os losangos indicam os melhores resultados do período."
    )

    # ==========================================================
    # MELHOR TREINO DOS FILTROS
    # ==========================================================

    dados_com_score_geral = dados_filtrados.dropna(
        subset=["score_geral"],
    )

    if dados_com_score_geral.empty:
        st.info(
            "Não há um treino com score geral válido "
            "para os filtros selecionados."
        )
        return

    indice_melhor = dados_com_score_geral[
        "score_geral"
    ].idxmax()

    melhor_treino = dados_com_score_geral.loc[
        indice_melhor
    ]

    st.write(
        "**🏆 Melhor treino dos filtros selecionados**"
    )

    col_melhor1, col_melhor2, col_melhor3, col_melhor4 = (
        st.columns(4)
    )

    col_melhor1.metric(
        "Mapa",
        melhor_treino["Cenario"],
    )

    col_melhor2.metric(
        "Score geral",
        f"{melhor_treino['score_geral']:.2f}",
    )

    col_melhor3.metric(
        "Precisão",
        (
            f"{melhor_treino['score_precisao']:.2f}"
            if pd.notna(melhor_treino["score_precisao"])
            else "N/A"
        ),
    )

    col_melhor4.metric(
        "Controle",
        (
            f"{melhor_treino['score_controle']:.2f}"
            if pd.notna(melhor_treino["score_controle"])
            else "N/A"
        ),
    )


if "Categoria" not in scores.columns or "Cenario" not in scores.columns:
    st.error(
        "As colunas 'Categoria' e 'Cenario' não chegaram ao Score Engine. "
        "Confira se o feature_engineering.py preserva essas colunas."
    )
else:
    aba_clicking, aba_tracking, aba_switching = st.tabs(
        [
            "🎯 Clicking",
            "🔄 Tracking",
            "⚡ Target Switching",
        ]
    )

    with aba_clicking:
        scores_clicking = scores[
            scores["Categoria"] == "Clicking"
        ].copy()

        criar_grafico_categoria(
            dados_categoria=scores_clicking,
            categoria="Clicking",
        )

    with aba_tracking:
        scores_tracking = scores[
            scores["Categoria"] == "Tracking"
        ].copy()

        criar_grafico_categoria(
            dados_categoria=scores_tracking,
            categoria="Tracking",
        )

    with aba_switching:
        scores_switching = scores[
            scores["Categoria"] == "Target Switching"
        ].copy()

        criar_grafico_categoria(
            dados_categoria=scores_switching,
            categoria="Target Switching",
        )

st.divider()


# ==========================================================
# RADAR DE HABILIDADES
# ==========================================================

st.subheader("🎯 Radar de habilidades")

habilidades_radar = [
    "Precisão",
    "Velocidade",
    "Controle",
    "Consistência",
]

valores_radar = [
    treino_atual["score_precisao"],
    treino_atual["score_velocidade"],
    treino_atual["score_controle"],
    treino_atual["score_consistencia"],
]

# Fecha o radar
habilidades_radar.append(habilidades_radar[0])
valores_radar.append(valores_radar[0])

fig_radar = go.Figure()

fig_radar.add_trace(
    go.Scatterpolar(
        r=valores_radar,
        theta=habilidades_radar,
        fill="toself",
        name="Treino atual",
        line=dict(width=3),
        hovertemplate=(
            "%{theta}<br>"
            "Score: %{r:.2f}"
            "<extra></extra>"
        ),
    )
)

fig_radar.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    polar=dict(
        bgcolor="#0E1117",
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickvals=[20, 40, 60, 80, 100],
        ),
    ),
    showlegend=False,
    height=550,
    margin=dict(
        l=50,
        r=50,
        t=50,
        b=50,
    ),
)

st.plotly_chart(
    fig_radar,
    width="stretch",
)