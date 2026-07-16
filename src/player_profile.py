import pandas as pd

from src.utils import log_aviso, log_info


def identificar_ponto_melhoria(features: pd.DataFrame) -> dict:
    """
    Identifica o principal aspecto que o jogador precisa melhorar.

    Retorna um dicionário com o aspecto, valor encontrado
    e uma breve explicação.
    """

    if features.empty:
        log_aviso("Nenhuma feature disponível para análise.")
        return {}

    # Usa o treino mais recente
    treino = features.iloc[-1]

    problemas = []

    accuracy = treino.get("accuracy_global")
    ttk = treino.get("ttk_medio")
    efficiency = treino.get("efficiency_media")
    overshots = treino.get("overshots_medio")
    consistencia = treino.get("consistencia_accuracy")

    if pd.notna(accuracy) and accuracy < 0.80:
        problemas.append(
            {
                "aspecto": "Precisão",
                "prioridade": 0.80 - accuracy,
                "valor": accuracy,
                "explicacao": "A precisão global está abaixo de 80%.",
            }
        )

    if pd.notna(ttk) and ttk > 0.50:
        problemas.append(
            {
                "aspecto": "Velocidade",
                "prioridade": ttk - 0.50,
                "valor": ttk,
                "explicacao": "O tempo médio para eliminar o alvo está elevado.",
            }
        )

    if pd.notna(efficiency) and efficiency < 0.70:
        problemas.append(
            {
                "aspecto": "Eficiência",
                "prioridade": 0.70 - efficiency,
                "valor": efficiency,
                "explicacao": "A eficiência média está abaixo de 70%.",
            }
        )

    if pd.notna(overshots) and overshots > 2:
        problemas.append(
            {
                "aspecto": "Controle de tiros",
                "prioridade": overshots / 10,
                "valor": overshots,
                "explicacao": "Há muitos disparos além do necessário.",
            }
        )

    if pd.notna(consistencia) and consistencia < 0.85:
        problemas.append(
            {
                "aspecto": "Consistência",
                "prioridade": 0.85 - consistencia,
                "valor": consistencia,
                "explicacao": "A precisão varia muito durante o treino.",
            }
        )

    if not problemas:
        resultado = {
            "aspecto": "Desempenho equilibrado",
            "prioridade": 0,
            "valor": None,
            "explicacao": "Nenhum ponto crítico foi identificado.",
        }

        log_info("Nenhum ponto crítico de melhoria identificado.")
        return resultado

    principal_problema = max(
        problemas,
        key=lambda problema: problema["prioridade"],
    )

    log_info(
        f"Principal ponto de melhoria: "
        f"{principal_problema['aspecto']}"
    )

    return principal_problema