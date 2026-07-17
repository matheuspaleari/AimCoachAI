from pathlib import Path


COLUNAS_DADOS_DETALHADOS = {
    "Kill #",
    "Timestamp",
    "Bot",
    "Weapon",
    "TTK",
    "Shots",
    "Hits",
    "Accuracy",
}

MARCADORES_ESTATISTICA = {
    "Kills:",
    "Deaths:",
    "Fight Time:",
    "Avg TTK:",
    "Damage Done:",
    "Hit Count:",
    "Miss Count:",
    "Weapon,Shots,Hits",
}


def identificar_tipo_csv(caminho_arquivo: Path) -> str:
    """
    Identifica o tipo do CSV.

    Retorna:
    - 'dados_detalhados'
    - 'estatisticas'
    - 'desconhecido'
    """

    try:
        with caminho_arquivo.open(
            mode="r",
            encoding="utf-8-sig",
            errors="ignore",
        ) as arquivo:
            linhas = [
                linha.strip()
                for linha in arquivo.readlines()[:30]
                if linha.strip()
            ]

    except OSError:
        return "desconhecido"

    if not linhas:
        return "desconhecido"

    conteudo_inicial = "\n".join(linhas)

    # Arquivo de estatísticas possui marcadores de resumo
    if any(
        marcador in conteudo_inicial
        for marcador in MARCADORES_ESTATISTICA
    ):
        return "estatisticas"

    # Verifica o cabeçalho detalhado
    cabecalho = {
        coluna.strip()
        for coluna in linhas[0].split(",")
    }

    possui_colunas_detalhadas = (
        COLUNAS_DADOS_DETALHADOS.issubset(cabecalho)
    )

    if not possui_colunas_detalhadas:
        return "desconhecido"

    # Confirma se existe pelo menos uma linha de kill válida
    for linha in linhas[1:]:
        primeira_coluna = linha.split(",", maxsplit=1)[0].strip()

        if primeira_coluna.isdigit():
            return "dados_detalhados"

    return "estatisticas"