from datetime import datetime, timedelta
from pathlib import Path
import math
import random

import pandas as pd


PASTA_SAIDA = Path("data/raw")

QUANTIDADE_TREINOS = 300
KILLS_POR_TREINO = 120

SEED = 42


def limitar(valor: float, minimo: float, maximo: float) -> float:
    """
    Mantém um valor dentro dos limites informados.
    """
    return max(minimo, min(maximo, valor))


def calcular_progresso(numero_treino: int) -> float:
    """
    Retorna um progresso entre 0 e 1.

    Usa uma curva exponencial para que o jogador melhore rapidamente
    no início e depois tenha uma evolução mais lenta.
    """

    return 1 - math.exp(-numero_treino / 110)


def gerar_oscilacao_sessao(numero_treino: int) -> float:
    """
    Cria pequenas fases de melhora e queda ao longo do histórico.
    """

    oscilacao_longa = math.sin(numero_treino / 14) * 0.025
    oscilacao_curta = math.sin(numero_treino / 5) * 0.012

    return oscilacao_longa + oscilacao_curta


def gerar_treino(numero_treino: int) -> pd.DataFrame:
    """
    Gera uma sessão sintética de treino.

    O jogador evolui ao longo do tempo, mas apresenta:
    - oscilações;
    - sessões ruins;
    - platôs;
    - limites realistas.
    """

    progresso = calcular_progresso(numero_treino)
    oscilacao = gerar_oscilacao_sessao(numero_treino)

    inicio = datetime(2026, 1, 1, 19, 0, 0) + timedelta(
        days=numero_treino - 1
    )

    # Evolução limitada e não linear
    accuracy_base = 0.62 + (0.28 * progresso) + oscilacao
    ttk_base = 0.82 - (0.40 * progresso) - (oscilacao * 0.5)
    overshots_base = 3.8 - (2.7 * progresso) - (oscilacao * 3)
    efficiency_base = 0.58 + (0.30 * progresso) + oscilacao

    # Algumas sessões naturalmente piores
    sessao_ruim = random.random() < 0.08

    if sessao_ruim:
        accuracy_base -= random.uniform(0.03, 0.08)
        ttk_base += random.uniform(0.04, 0.12)
        overshots_base += random.uniform(0.4, 1.2)
        efficiency_base -= random.uniform(0.03, 0.08)

    accuracy_base = limitar(accuracy_base, 0.50, 0.93)
    ttk_base = limitar(ttk_base, 0.32, 0.90)
    overshots_base = limitar(overshots_base, 0.45, 4.5)
    efficiency_base = limitar(efficiency_base, 0.50, 0.92)

    linhas = []
    horario_atual = inicio

    armas = [
        "pistol",
        "rifle",
        "smg",
    ]

    for kill in range(1, KILLS_POR_TREINO + 1):
        accuracy_estimativa = limitar(
            random.gauss(accuracy_base, 0.09),
            0.30,
            1.0,
        )

        shots = random.randint(1, 6)

        hits = round(shots * accuracy_estimativa)
        hits = limitar(hits, 1, shots)

        accuracy_real = hits / shots

        ttk = limitar(
            random.gauss(ttk_base, 0.10),
            0.18,
            1.20,
        )

        overshots = max(
            0,
            round(random.gauss(overshots_base, 0.9)),
        )

        efficiency = limitar(
            random.gauss(efficiency_base, 0.08),
            0.25,
            1.0,
        )

        damage_possible = 50.0

        damage_done = limitar(
            damage_possible * efficiency,
            0,
            damage_possible,
        )

        intervalo = random.uniform(0.4, 1.8)
        horario_atual += timedelta(seconds=intervalo)

        linhas.append(
            {
                "Kill #": kill,
                "Timestamp": horario_atual.strftime(
                    "%H:%M:%S.%f"
                )[:-3],
                "Bot": "target",
                "Weapon": random.choice(armas),
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


def limpar_dados_antigos() -> None:
    """
    Remove apenas os CSVs sintéticos antigos.
    """

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    for arquivo in PASTA_SAIDA.glob("treino_*.csv"):
        arquivo.unlink()


def main() -> None:
    random.seed(SEED)

    limpar_dados_antigos()

    for numero in range(1, QUANTIDADE_TREINOS + 1):
        dados = gerar_treino(numero)

        nome_arquivo = (
            PASTA_SAIDA / f"treino_{numero:03d}.csv"
        )

        dados.to_csv(
            nome_arquivo,
            index=False,
            encoding="utf-8-sig",
        )

        print(
            f"Criado: {nome_arquivo.name} "
            f"({len(dados)} registros)"
        )

    print("\nBase sintética criada com sucesso.")
    print(f"Treinos gerados: {QUANTIDADE_TREINOS}")
    print(
        "Registros totais: "
        f"{QUANTIDADE_TREINOS * KILLS_POR_TREINO}"
    )


if __name__ == "__main__":
    main()