from datetime import datetime


def log_info(mensagem: str) -> None:
    horario = datetime.now().strftime("%H:%M:%S")
    print(f"[INFO {horario}] {mensagem}")


def log_aviso(mensagem: str) -> None:
    horario = datetime.now().strftime("%H:%M:%S")
    print(f"[AVISO {horario}] {mensagem}")


def log_erro(mensagem: str) -> None:
    horario = datetime.now().strftime("%H:%M:%S")
    print(f"[ERRO {horario}] {mensagem}")