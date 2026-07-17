import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
import pandas as pd


# ==========================================================
# CONFIGURAÇÃO DE IMPORTAÇÃO
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


from src.feature_engineering import criar_features_treino
from src.insights_engine import gerar_insights
from src.load_data import carregar_dados
from src.performance_engine import analisar_performance
from src.player_profile import gerar_perfil_jogador
from src.preprocessing import limpar_dados
from src.score_engine import calcular_scores
from src.coach_ai import gerar_recomendacao_coach


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
    Executa o pipeline completo de análise do AimCoachAI.
    """

    dados = carregar_dados()

    if dados.empty:
        return None, None, None, None, None

    dados_limpos = limpar_dados(dados)

    if dados_limpos.empty:
        return None, None, None, None, None

    features = criar_features_treino(dados_limpos)

    if features.empty:
        return None, None, None, None, None

    scores = calcular_scores(features)

    if scores.empty:
       return None, None, None, None, None

    analise = analisar_performance(scores)

    if not analise:
        return None, None, None, None, None

    insights = gerar_insights(analise)

    if not insights:
        return None, None, None, None, None

    perfil = gerar_perfil_jogador(scores)

    if not perfil:
        return None, None, None, None, None

    recomendacao = gerar_recomendacao_coach(
        scores=scores,
        analise=analise,
        perfil=perfil,
)

    if not recomendacao:
        return None, None, None, None, None

    return scores, analise, insights, perfil, recomendacao


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
# TÍTULO
# ==========================================================

st.title("🎯 AimCoachAI")

st.caption(
    "Plataforma inteligente para análise de desempenho "
    "em treinos de mira."
)


# ==========================================================
# EXECUÇÃO DO PIPELINE
# ==========================================================

scores, analise, insights, perfil, recomendacao = executar_pipeline()

if scores is None:
    st.warning(
        "Não foi possível carregar os dados ou gerar as análises. "
        "Confira se existem arquivos CSV em data/raw."
    )
    st.stop()


treino_atual = scores.iloc[-1]
resumo = analise["resumo"]


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
# COACH AI
# ==========================================================

with st.expander(
    "🧠 Coach AI • Plano de treino personalizado",
    expanded=True,
):
    col_coach1, col_coach2, col_coach3 = st.columns(3)

    col_coach1.metric("Habilidade prioritária", recomendacao["habilidade_prioritaria"])
    col_coach2.metric("Prioridade", recomendacao["prioridade"])
    col_coach3.metric("Tempo sugerido", f"{recomendacao['duracao_total_minutos']} minutos")

    st.write("**Objetivo principal**")
    st.info(recomendacao["objetivo_principal"])

    st.write("**📋 Plano da sessão**")

    exercicios_concluidos = []

    for ordem, exercicio in enumerate(recomendacao["exercicios"], start=1):

        col_check, col_exercicio, col_tempo, col_objetivo = st.columns([0.5,2.5,1,4])

        with col_check:
            concluido = st.checkbox("", key=f"coach_exercicio_{ordem}")

        with col_exercicio:
            st.markdown(f"**{ordem}️⃣ 🎯 {exercicio['nome']}**")

        with col_tempo:
            st.markdown(f"⏱ **{exercicio['duracao_minutos']} min**")

        with col_objetivo:
            st.caption(exercicio["foco"])

        exercicios_concluidos.append(concluido)

    quantidade_concluida = sum(exercicios_concluidos)
    quantidade_total = len(exercicios_concluidos)

    progresso = quantidade_concluida / quantidade_total if quantidade_total else 0

    st.progress(
        progresso,
        text=f"Sessão concluída: {quantidade_concluida}/{quantidade_total} exercícios",
    )

    if quantidade_concluida == quantidade_total:
        st.success("✅ Sessão concluída! Excelente trabalho.")

    meta = recomendacao["meta"]

    st.write("**Meta de curto prazo**")
    st.success(
        f"{meta['habilidade']}: {meta['score_atual']:.2f} → {meta['score_meta']:.2f} (+{meta['ganho_necessario']:.2f})"
    )

    st.write("**Por que essa recomendação?**")
    st.info(recomendacao["explicacao"])


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

st.error(resumo["principal_ponto_atual"])

st.divider()


# ==========================================================
# EVOLUÇÃO DAS HABILIDADES
# ==========================================================

st.subheader("📈 Evolução das habilidades")

nomes_habilidades = {
    "precisao": "Precisão",
    "velocidade": "Velocidade",
    "controle": "Controle de tiros",
    "consistencia": "Consistência",
}

colunas_evolucao = st.columns(4)

for indice, (chave, nome) in enumerate(nomes_habilidades.items()):
    resultado = analise[chave]

    colunas_evolucao[indice].metric(
        nome,
        f"{resultado['score_atual']:.2f}",
        f"{resultado['variacao_total_percentual']:.2f}%",
    )

st.divider()


# ==========================================================
# INSIGHTS
# ==========================================================

with st.expander(
    "💡 Insights e conclusão",
    expanded=True,
):
    st.subheader("Insights")

    for insight in insights["habilidades"].values():
        st.info(insight["mensagem"])

    st.subheader("Conclusão")

    for conclusao in insights["conclusoes"]:
        st.write(f"✅ {conclusao}")



# ==========================================================
# FILTRO DO HISTÓRICO
# ==========================================================

st.subheader("📈 Histórico de evolução")

col_filtro1, col_filtro2 = st.columns([1, 3])

with col_filtro1:
    periodo_selecionado = st.selectbox(
        "Período analisado",
        [
            "Últimos 10 treinos",
            "Últimos 30 treinos",
            "Últimos 50 treinos",
            "Últimos 100 treinos",
            "Todo o histórico",
        ],
        index=3,
    )

scores_filtrados = filtrar_periodo(
    scores=scores,
    periodo_selecionado=periodo_selecionado,
)

with col_filtro2:
    st.metric(
        "Treinos exibidos",
        len(scores_filtrados),
        help="Quantidade de treinos exibidos no gráfico.",
    )


# ==========================================================
# PREPARAÇÃO DO HISTÓRICO
# ==========================================================

historico = scores_filtrados.set_index("Treino")[
    [
        "score_precisao",
        "score_velocidade",
        "score_controle",
        "score_consistencia",
        "score_geral",
    ]
]

# Média móvel exponencial
historico_ema = historico.ewm(
    span=min(20, max(2, len(historico))),
    adjust=False,
).mean()

# Melhor resultado de cada habilidade no período selecionado
melhores = {
    "score_precisao": historico["score_precisao"].idxmax(),
    "score_velocidade": historico["score_velocidade"].idxmax(),
    "score_controle": historico["score_controle"].idxmax(),
    "score_consistencia": historico["score_consistencia"].idxmax(),
    "score_geral": historico["score_geral"].idxmax(),
}

fig = go.Figure()


# ==========================================================
# FUNÇÃO PARA ADICIONAR HABILIDADES AO GRÁFICO
# ==========================================================

def adicionar_habilidade(
    coluna: str,
    nome: str,
    largura_tendencia: int = 4,
    tamanho_melhor: int = 12,
):
    """
    Adiciona ao gráfico:
    - linha real translúcida;
    - linha EMA;
    - marcador do melhor resultado.
    """

    melhor_treino = melhores[coluna]
    melhor_valor = historico.loc[melhor_treino, coluna]

    # Linha real
    fig.add_trace(
        go.Scatter(
            x=historico.index,
            y=historico[coluna],
            mode="lines",
            name=nome,
            opacity=0.18,
            line=dict(width=1),
            hovertemplate=(
            f"{nome}: %{{y:.2f}}"
            "<extra></extra>"
            ),
        )
    )

    # Linha de tendência
    fig.add_trace(
        go.Scatter(
            x=historico.index,
            y=historico_ema[coluna],
            mode="lines",
            showlegend=False,
            line=dict(width=largura_tendencia),
            hoverinfo="skip",
        )
    )

    # Melhor resultado
    fig.add_trace(
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


# ==========================================================
# ADICIONA AS HABILIDADES
# ==========================================================

adicionar_habilidade(
    coluna="score_precisao",
    nome="🎯 Precisão",
)

adicionar_habilidade(
    coluna="score_velocidade",
    nome="⚡ Velocidade",
)

adicionar_habilidade(
    coluna="score_controle",
    nome="🔫 Controle",
)

adicionar_habilidade(
    coluna="score_consistencia",
    nome="📊 Consistência",
)

adicionar_habilidade(
    coluna="score_geral",
    nome="⭐ Score Geral",
    largura_tendencia=6,
    tamanho_melhor=15,
)


# ==========================================================
# CONFIGURAÇÃO DO GRÁFICO
# ==========================================================

fig.update_layout(
    title=(
        "Evolução das habilidades — "
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
    fig,
    width="stretch",
)

st.caption(
    "As linhas transparentes representam os resultados reais. "
    "As linhas fortes representam a tendência calculada pela EMA. "
    "Os losangos indicam os melhores resultados do período."
)

st.divider()


# ==========================================================
# MELHOR TREINO DO PERÍODO
# ==========================================================

st.subheader("🏆 Melhor treino do período")

melhor_treino_periodo = scores_filtrados.loc[
    scores_filtrados["score_geral"].idxmax()
]

col_melhor1, col_melhor2, col_melhor3, col_melhor4 = st.columns(4)

col_melhor1.metric(
    "Treino",
    melhor_treino_periodo["Treino"],
)

col_melhor2.metric(
    "Score geral",
    f"{melhor_treino_periodo['score_geral']:.2f}",
)

col_melhor3.metric(
    "Precisão",
    f"{melhor_treino_periodo['score_precisao']:.2f}",
)

col_melhor4.metric(
    "Controle",
    f"{melhor_treino_periodo['score_controle']:.2f}",
)

st.success(
    f"Este foi o melhor treino dentro do período: "
    f"{periodo_selecionado}."
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