# 🎯 AimCoachAI

Sistema inteligente para análise de desempenho em Aim Trainers utilizando Engenharia de Dados, Analytics, Visualização de Dados e Inteligência Artificial.

O objetivo do projeto é transformar arquivos CSV gerados por jogos e softwares de treino de mira em análises inteligentes, permitindo acompanhar a evolução do jogador, identificar pontos fracos e recomendar melhorias.

---

# 🚀 Objetivos

O AimCoachAI foi desenvolvido para responder perguntas como:

- 📈 O jogador está evoluindo?
- 🎯 Qual habilidade precisa de mais treino?
- ⚡ A velocidade está melhorando?
- 🔫 O controle dos disparos evoluiu?
- 📊 O desempenho atual está acima da média histórica?
- 🏆 Qual foi o melhor treino realizado?

---

# 🛠 Tecnologias Utilizadas

- 🐍 Python
- 🐼 Pandas
- 📊 Plotly
- 🎨 Streamlit
- 📈 Machine Learning (em desenvolvimento)
- 📂 CSV
- 💻 VS Code

---

# 📂 Estrutura do Projeto

```text
AimCoachAI
│
├── app/
│   └── streamlit_app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│
├── notebooks/
│
├── reports/
│
├── src/
│   ├── config.py
│   ├── feature_engineering.py
│   ├── insights_engine.py
│   ├── load_data.py
│   ├── performance_engine.py
│   ├── player_profile.py
│   ├── preprocessing.py
│   ├── recommendation.py
│   ├── save_data.py
│   ├── score_engine.py
│   ├── utils.py
│   └── visualization.py
│
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# ⚙ Pipeline

```text
Arquivos CSV

        │

        ▼

Carregamento dos dados

        │

        ▼

Limpeza e tratamento

        │

        ▼

Feature Engineering

        │

        ▼

Score Engine

        │

        ▼

Performance Engine

        │

        ▼

Insights Engine

        │

        ▼

Dashboard Streamlit
```

---

# 📊 Funcionalidades

## 📥 Carregamento

- Leitura automática de múltiplos CSVs
- Histórico completo do jogador
- Consolidação dos treinos

---

## 🧹 Pré-processamento

- Limpeza de registros inválidos
- Conversão de tipos
- Padronização dos dados
- Tratamento de valores ausentes

---

## ⚙ Feature Engineering

Extração de métricas como:

- Accuracy média
- Accuracy global
- TTK médio
- Consistência
- Kills por minuto
- Overshots
- Dano desperdiçado
- Kills perfeitos
- Tempo total de treino

---

## 🏆 Score Engine

Cada treino recebe uma pontuação para diferentes habilidades.

Atualmente são avaliadas:

- 🎯 Precisão
- ⚡ Velocidade
- 🔫 Controle dos disparos
- 📊 Consistência

Além disso é calculado:

- ⭐ Score Geral

---

## 📈 Performance Engine

Analisa a evolução do jogador.

Inclui:

- Média histórica
- Melhor treino
- Pior treino
- Tendência de evolução
- Crescimento percentual
- Habilidades em queda

---

## 💡 Insights Engine

Transforma métricas em linguagem natural.

Exemplo:

> Controle de tiros apresenta melhora nos treinos recentes.
>
> Está acima da média histórica.
>
> Evoluiu 95% desde o primeiro treino.

---

## 📊 Dashboard

Dashboard desenvolvido em Streamlit contendo:

- 📈 Histórico de evolução
- 🎯 Radar de habilidades
- ⭐ Score Geral
- 📊 Métricas principais
- 💡 Insights automáticos

---

# 🎯 Exemplo de Dashboard

O sistema apresenta informações como:

- Score Geral
- Precisão
- Velocidade
- Controle
- Consistência
- Evolução histórica
- Radar das habilidades
- Principal ponto de melhoria

---

# 📌 Próximas Funcionalidades

- 🤖 Recommendation Engine
- 👤 Perfil automático do jogador
- 🧠 Machine Learning para previsão de desempenho
- 📄 Exportação de relatórios em PDF
- ☁ Upload de CSV diretamente pelo Dashboard
- 📈 Comparação entre sessões
- 🎮 Suporte para diferentes Aim Trainers

---

# 📚 Objetivos de Aprendizagem

Este projeto foi desenvolvido para praticar conceitos de:

- Engenharia de Dados
- Análise Exploratória
- Feature Engineering
- Visualização de Dados
- Arquitetura de Software
- Machine Learning
- Streamlit
- Plotly
- Python

---

# 👨‍💻 Autor

**Matheus Paleari**

GitHub:
https://github.com/matheuspaleari