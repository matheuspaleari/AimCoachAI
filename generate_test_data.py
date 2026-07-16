from pathlib import Path
from datetime import datetime, timedelta
import random

import pandas as pd


PASTA_SAIDA = Path("data/raw")
QUANTIDADE_TREINOS = 12
KILLS_POR_TREINO = 120


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def gerar_treino(numero_treino: int) -> pd.DataFrame:
    """
    Gera um CSV sintético representando uma sessão de treino.

    Os dados simulam uma melhora gradual do jogador.
    """

    inicio = datetime(2026, 7, 1, 19, 0, 0) + timedelta(
        days=numero_treino - 1
    )

    linhas = []

    # Melhora gradual ao longo das sessões
    accuracy_base = 0.68 + numero_treino * 0.012
    ttk_base = 0.70 - numero_treino * 0.018
    overshots_base = 3.5 - numero_treino * 0.18

    horario_atual = inicio

    for kill in range(1, KILLS_POR_TREINO + 1):
        accuracy = limitar(
            random.gauss(accuracy_base, 0.08),
            0.35,
            1.0,
        )

        shots = random.randint(1, 5)
        hits = max(1, round(shots * accuracy))

        accuracy_real = hits / shots

        ttk = limitar(
            random.gauss(ttk_base, 0.10),
            0.18,
            1.20,
        )

        overshots = max(
            0,
            round(random.gauss(overshots_base, 1.0)),
        )

        damage_possible = 50.0
        damage_done = limitar(
            damage_possible * accuracy_real,
            0,
            damage_possible,
        )

        efficiency = damage_done / damage_possible

        intervalo = random.uniform(0.3, 1.5)
        horario_atual += timedelta(seconds=intervalo)

        linhas.append(
            {
                "Kill #": kill,
                "Timestamp": horario_atual.strftime("%H:%M:%S.%f")[:-3],
                "Bot": "target",
                "Weapon": random.choice(
                    ["pistol", "rifle", "smg"]
                ),
                "TTK": f"{ttk:.6f}s",
                "Shots": float(shots),
                "Hits": float(hits),
                "Accuracy": round(accuracy_real, 4),
                "Damage Done": round(damage_done, 2),
                "Damage Possible": damage_possible,
                "Efficiency": round(efficiency, 4),
                "Cheated": 0.0,
                "OverShots": float(overshots),
            }
        )

    return pd.DataFrame(linhas)


def main():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    for numero in range(1, QUANTIDADE_TREINOS + 1):
        dados = gerar_treino(numero)

        nome_arquivo = PASTA_SAIDA / f"treino_{numero:02d}.csv"

        dados.to_csv(
            nome_arquivo,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"Criado: {nome_arquivo}")

    print("\nBase de teste criada com sucesso.")


if __name__ == "__main__":
    main()