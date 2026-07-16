import sys
from pathlib import Path
import plotly.graph_objects as go
import streamlit as st

# Permite importar os módulos da pasta src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.feature_engineering import criar_features_treino
from src.insights_engine import gerar_insights
from src.load_data import carregar_dados
from src.performance_engine import analisar_performance
from src.preprocessing import limpar_dados
from src.score_engine import calcular_scores


st.set_page_config(
    page_title="AimCoachAI",
    page_icon="🎯",
    layout="wide",
)


def executar_pipeline():
    dados = carregar_dados()

    if dados.empty:
        return None, None, None

    dados_limpos = limpar_dados(dados)

    if dados_limpos.empty:
        return None, None, None

    features = criar_features_treino(dados_limpos)

    if features.empty:
        return None, None, None

    scores = calcular_scores(features)

    if scores.empty:
        return None, None, None

    analise = analisar_performance(scores)
    insights = gerar_insights(analise)

    return scores, analise, insights


st.title("🎯 AimCoachAI")
st.caption("Análise inteligente de desempenho em treinos de mira")

scores, analise, insights = executar_pipeline()

if scores is None:
    st.warning(
        "Nenhum arquivo CSV foi encontrado. "
        "Adicione os arquivos na pasta data/raw."
    )
    st.stop()

treino_atual = scores.iloc[-1]
resumo = analise["resumo"]

st.subheader("Resumo do treino atual")

coluna1, coluna2, coluna3, coluna4, coluna5 = st.columns(5)

coluna1.metric(
    "Score geral",
    f"{treino_atual['score_geral']:.2f}",
)

coluna2.metric(
    "Precisão",
    f"{treino_atual['score_precisao']:.2f}",
)

coluna3.metric(
    "Velocidade",
    f"{treino_atual['score_velocidade']:.2f}",
)

coluna4.metric(
    "Controle",
    f"{treino_atual['score_controle']:.2f}",
)

coluna5.metric(
    "Consistência",
    f"{treino_atual['score_consistencia']:.2f}",
)

st.divider()

st.subheader("Principal ponto de melhoria")

st.error(
    f"🎯 {resumo['principal_ponto_atual']}"
)

st.divider()

st.subheader("Evolução das habilidades")

nomes_habilidades = {
    "precisao": "Precisão",
    "velocidade": "Velocidade",
    "controle": "Controle de tiros",
    "consistencia": "Consistência",
}

colunas = st.columns(4)

for indice, (chave, nome) in enumerate(nomes_habilidades.items()):
    resultado = analise[chave]

    colunas[indice].metric(
        nome,
        f"{resultado['score_atual']:.2f}",
        f"{resultado['variacao_total_percentual']:.2f}%",
    )

st.divider()

st.subheader("Insights")

for insight in insights["habilidades"].values():
    st.info(insight["mensagem"])

st.subheader("Conclusão")

for conclusao in insights["conclusoes"]:
    st.write(f"✅ {conclusao}")

st.divider()

st.subheader("📈 Histórico de evolução")

historico = scores.set_index("Treino")[
    [
        "score_precisao",
        "score_velocidade",
        "score_controle",
        "score_consistencia",
        "score_geral",
    ]
]

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=historico.index,
        y=historico["score_precisao"],
        mode="lines+markers",
        name="🎯 Precisão",
        line=dict(width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=historico.index,
        y=historico["score_velocidade"],
        mode="lines+markers",
        name="⚡ Velocidade",
        line=dict(width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=historico.index,
        y=historico["score_controle"],
        mode="lines+markers",
        name="🔫 Controle",
        line=dict(width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=historico.index,
        y=historico["score_consistencia"],
        mode="lines+markers",
        name="📊 Consistência",
        line=dict(width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=historico.index,
        y=historico["score_geral"],
        mode="lines+markers",
        name="⭐ Score Geral",
        line=dict(width=5, dash="solid"),
    )
)

fig.update_layout(
    title="Evolução das habilidades ao longo dos treinos",
    xaxis_title="Treinos",
    yaxis_title="Score",
    yaxis=dict(range=[0, 100]),
    hovermode="x unified",
    template="plotly_dark",
    height=550,

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=13),
    ),
)
st.plotly_chart(
    fig,
    width="stretch",
)
st.divider()

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

# Repete o primeiro item para fechar o radar
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
    )
)

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickvals=[20, 40, 60, 80, 100],
        )
    ),
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="center",
        x=0.5,
    ),
    height=550,
    margin=dict(
        l=60,
        r=60,
        t=80,
        b=40,
    ),
)

st.plotly_chart(
    fig_radar,
    width="stretch",
)