import time


def countdown_timer(wait_seconds: int, msg_wait=""):
    """Conta por segundos"""

    for i in range(wait_seconds, 0, -1):
        print(f"{msg_wait} {i} segundo(s)...{' '*10}", end='\r')
        time.sleep(1)  # Espera 1 segundo

    # Encerramento
    print(' '*100, end='\r')
