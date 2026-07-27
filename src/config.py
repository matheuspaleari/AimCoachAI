from pathlib import Path


# Pasta principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Pastas de dados
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Arquivo de dados tratados
HISTORICO_LIMPO_PATH = (
    PROCESSED_DATA_DIR / "historico_limpo.csv"
)

# Pasta e arquivo do modelo
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "random_forest.pkl"

# Colunas obrigatórias esperadas nos CSVs
COLUNAS_OBRIGATORIAS = [
    "Kill #",
    "Timestamp",
    "Bot",
    "Weapon",
    "TTK",
    "Shots",
    "Hits",
    "Accuracy",
    "Damage Done",
    "Damage Possible",
    "Efficiency",
    "Cheated",
    "OverShots",
]

# Colunas que devem ser convertidas para número
COLUNAS_NUMERICAS = [
    "Shots",
    "Hits",
    "Accuracy",
    "Damage Done",
    "Damage Possible",
    "Efficiency",
    "Cheated",
    "OverShots",
]

# ==========================================================
# PESOS DO SCORE POR CATEGORIA
# ==========================================================

PESOS_CATEGORIA = {

    "Clicking": {
        "precisao": 0.45,
        "velocidade": 0.30,
        "controle": 0.15,
        "consistencia": 0.10,
    },

    "Tracking": {
        "precisao": 0.20,
        "velocidade": 0.20,
        "controle": 0.40,
        "consistencia": 0.20,
    },

    "Target Switching": {
        "precisao": 0.30,
        "velocidade": 0.35,
        "controle": 0.20,
        "consistencia": 0.15,
    },

}