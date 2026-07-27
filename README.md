# 🎯 AimCoachAI

<p align="center">

Sistema inteligente para análise de desempenho em **Aim Trainers**, utilizando **Engenharia de Dados**, **Data Analytics**, **Visualização de Dados** e **Inteligência Artificial** para acompanhar a evolução do jogador.

</p>

---

## 📸 Dashboard

<img width="1753" height="743" alt="image" src="https://github.com/user-attachments/assets/4258731c-024f-44fd-951f-55b685907253" />


</p>

---

## 🚀 Sobre o Projeto

O **AimCoachAI** transforma os arquivos CSV gerados por Aim Trainers em análises inteligentes de desempenho.

A plataforma calcula métricas avançadas, identifica padrões de evolução, gera insights automáticos e recomenda planos personalizados de treino através do **Coach AI**.

O objetivo é permitir que qualquer jogador acompanhe sua evolução da mesma forma que plataformas como **Tracker.gg**, **Blitz** ou **OP.GG**, porém focado em treinamento de mira.

---

# ✨ Funcionalidades

## 📥 Importação automática

- Leitura de múltiplos CSVs
- Histórico completo do jogador
- Consolidação automática dos treinos

---

## 🧹 Pré-processamento

- Remoção de registros inválidos
- Conversão automática de tipos
- Tratamento de valores ausentes
- Padronização dos dados

---

## ⚙ Feature Engineering

Extração automática de dezenas de métricas:

- 🎯 Accuracy Global
- ⚡ TTK Médio
- 📊 Consistência
- 🔫 Controle dos disparos
- 💥 Overshots
- 🎯 Kills perfeitos
- 📈 Kills por minuto
- 💣 Dano desperdiçado
- ⏱ Tempo total de treino

---

## 🏆 Score Engine

Cada treino recebe uma pontuação entre **0 e 100** para:

- 🎯 Precisão
- ⚡ Velocidade
- 🔫 Controle
- 📊 Consistência

Além disso é calculado:

⭐ Score Geral

---

## 👤 Player Profile

Classificação automática do jogador.

Exemplo:

```
🟡 Ouro

🎮 Control Player

Especialidade:
Controle dos disparos

Principal ponto de melhoria:
Consistência
```

---

## 🧠 Coach AI

O sistema gera automaticamente:

- habilidade prioritária
- prioridade do treino
- objetivo principal
- plano personalizado
- tempo recomendado
- meta de evolução
- explicação do motivo da recomendação

Exemplo:

```
Prioridade:
🔴 Crítica

Objetivo:
Aumentar velocidade de aquisição de alvos.

Plano:

Gridshot
12 min

Spidershot Speed
12 min

Microflex
11 min
```

---

## 🏅 Sistema de XP

Cada treino gera experiência.

O jogador evolui automaticamente pelos elos:

```
⚫ Ferro

🟤 Bronze

⚪ Prata

🟡 Ouro

🟢 Platina

🔷 Diamante

🟣 Ascendente

🔴 Imortal

☀️ Radiante
```

Quanto maior o elo, maior será a quantidade de XP necessária para evoluir.

---

## 📈 Performance Engine

Analisa automaticamente:

- evolução histórica
- tendência
- crescimento
- regressão
- média histórica dinâmica
- melhor treino
- pior treino
- comparação entre períodos

---

## 💡 Insights Engine

Transforma métricas em linguagem natural.

Exemplo:

```
Precisão apresenta evolução consistente.

Velocidade caiu nos treinos recentes.

Controle permanece estável.

Consistência está acima da média histórica.
```

---

# 📊 Dashboard Premium

O dashboard apresenta:

- 🏅 Sistema de XP
- 👤 Perfil do jogador
- 🧠 Coach AI
- 📊 Resumo do treino
- 📈 Evolução histórica
- 📉 Evolução por categoria
- 🎯 Radar de habilidades
- 💡 Insights automáticos
- 📈 Progressão dos elos

---

# 🏗 Arquitetura

```
CSV

        │

        ▼

Pré-processamento

        │

        ▼

Feature Engineering

        │

        ▼

Janela Histórica

        │

        ▼

Map Statistics

        │

        ▼

Score Engine

        │

        ▼

Player Profile

        │

        ▼

Performance Engine

        │

        ▼

Insights Engine

        │

        ▼

Coach AI

        │

        ▼

XP Engine

        │

        ▼

Dashboard Premium
```

---

# 📂 Estrutura

```
AimCoachAI

app/
    streamlit_app.py

src/

    coach_ai.py
    feature_engineering.py
    history_window.py
    insights_engine.py
    load_data.py
    map_statistics.py
    performance_engine.py
    player_profile.py
    preprocessing.py
    score_engine.py
    utils.py
    xp_engine.py

data/

    raw/
    processed/

models/

reports/

tests/

README.md
requirements.txt
main.py
```

---

# 🛠 Tecnologias

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Scikit-Learn
- Machine Learning
- Engenharia de Dados
- Data Analytics
- Git
- GitHub

---

# 📈 Estatísticas do Projeto

✔ Mais de **120 mil registros** processados

✔ Mais de **900 sessões** analisadas

✔ Sistema próprio de Score

✔ Sistema próprio de XP

✔ Sistema próprio de Progressão

✔ Coach AI

✔ Dashboard Premium

✔ Insights automáticos

✔ Radar de habilidades

---

# 📌 Roadmap

## ✅ Concluído

- Score Engine
- Performance Engine
- Player Profile
- Coach AI
- Sistema de XP
- Progressão por Elos
- Dashboard Premium
- Insights Automáticos
- Radar
- Histórico por Categoria

---

## 🚧 Em desenvolvimento

- Upload de CSV pelo Dashboard
- Machine Learning para previsão de desempenho
- Comparação entre jogadores
- Banco de Dados
- API REST
- Sistema de Login
- Exportação PDF
- Ranking Global
- Integração automática com KovaaK's

---

# 🎯 Objetivos de Aprendizagem

Este projeto foi desenvolvido para aprofundar conhecimentos em:

- Engenharia de Dados
- Python
- Pandas
- Estatística
- Feature Engineering
- Visualização de Dados
- Arquitetura de Software
- Inteligência Artificial
- Machine Learning
- Streamlit
- Plotly

---

# 👨‍💻 Autor

## Matheus Paleari

🔗 GitHub

https://github.com/matheuspaleari

---

⭐ Se este projeto foi útil para você, considere deixar uma estrela no repositório.
