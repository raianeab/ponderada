"""
versao2.py - A4 versao 2: buffer circular com semaforos.

Ponderada CC08 (Tato) - Raiane Araujo Brandao (N = 7)

Tres semaforos:
    vazio (inicia em N) - posicoes livres
    cheio (inicia em 0) - amostras disponiveis
    mutex (inicia em 1) - exclusao mutua no buffer e nos indices

O consumidor usa acquire com timeout apenas para conseguir registrar um
travamento, caso ocorra.

Como rodar:  python3 versao2.py
"""

import threading
import time

from comum import N, TOTAL, TIMEOUT, EXECUCOES, analisar, imprimir_execucao, cabecalho


class Estado:
    """
    Estado compartilhado de uma execucao.

    Atributos:
        buffer (list): buffer circular de N posicoes.
        vazio, cheio, mutex (threading.Semaphore): semaforos descritos acima.
        recebidas (list[int]): amostras lidas pelo consumidor.
        travou (bool): o consumidor excedeu TIMEOUT em algum acquire.
    """

    def __init__(self):
        """Inicializa o buffer e os semaforos."""
        self.buffer = [None] * N
        self.vazio = threading.Semaphore(N)
        self.cheio = threading.Semaphore(0)
        self.mutex = threading.Semaphore(1)
        self.recebidas = []
        self.travou = False


def produtor(est):
    """
    Thread do sensor: insere as amostras 0..TOTAL-1 no buffer.

    Parametros:
        est (Estado): estado compartilhado.

    Retorno:
        None.
    """
    entrada = 0
    for amostra in range(TOTAL):
        # vazio antes de mutex: se o buffer estiver cheio, o produtor
        # bloqueia sem segurar o mutex, e o consumidor continua lendo.
        est.vazio.acquire()
        est.mutex.acquire()
        est.buffer[entrada] = amostra
        time.sleep(0)                     # mesma interrupcao da versao 1, agora protegida
        entrada = (entrada + 1) % N
        est.mutex.release()
        est.cheio.release()


def consumidor(est):
    """
    Thread do motor: retira TOTAL amostras do buffer.

    Parametros:
        est (Estado): estado compartilhado.

    Retorno:
        None. O resultado fica em est.recebidas e est.travou.
    """
    saida = 0
    for _ in range(TOTAL):
        if not est.cheio.acquire(timeout=TIMEOUT):
            est.travou = True
            return
        if not est.mutex.acquire(timeout=TIMEOUT):
            est.cheio.release()           # devolve o permit ja adquirido
            est.travou = True
            return
        est.recebidas.append(est.buffer[saida])
        time.sleep(0)
        saida = (saida + 1) % N
        est.mutex.release()
        est.vazio.release()


def executar(numero):
    """
    Executa uma rodada da versao 2 e imprime o resultado.

    Parametros:
        numero (int): numero da execucao.

    Retorno:
        tuple(dict, bool): metricas de analisar() e se travou.
    """
    est = Estado()
    tp = threading.Thread(target=produtor, args=(est,), daemon=True)
    tc = threading.Thread(target=consumidor, args=(est,), daemon=True)
    inicio = time.monotonic()
    tc.start()
    tp.start()
    tc.join()
    tp.join(timeout=2)
    tempo = time.monotonic() - inicio
    stats = analisar(est.recebidas)
    imprimir_execucao(2, numero, stats, est.travou, tempo)
    return stats, est.travou


def main():
    """Executa as EXECUCOES rodadas da versao 2."""
    cabecalho(2, "com semaforos vazio/cheio/mutex")
    for i in range(1, EXECUCOES + 1):
        executar(i)


if __name__ == "__main__":
    main()
