"""
versao3.py - A4 versao 3: semaforos com a ordem trocada no produtor.

Ponderada CC08 (Tato) - Raiane Araujo Brandao (N = 7)

Igual a versao 2, mas o produtor faz wait(mutex) antes de wait(vazio).
Se o produtor tentar inserir com o buffer cheio, ele bloqueia em vazio
segurando o mutex, e o consumidor bloqueia no mutex. Em qual amostra isso
acontece depende do escalonador.

A thread do produtor fica bloqueada indefinidamente apos o deadlock, por
isso e criada como daemon.

Como rodar:  python3 versao3.py
"""

import threading
import time

from comum import N, TOTAL, TIMEOUT, EXECUCOES, analisar, imprimir_execucao, cabecalho


class Estado:
    """
    Estado compartilhado de uma execucao.

    Atributos:
        buffer (list): buffer circular de N posicoes.
        vazio, cheio, mutex (threading.Semaphore): iguais aos da versao 2.
        recebidas (list[int]): amostras lidas pelo consumidor.
        produzidas (int): amostras que o produtor conseguiu inserir.
        travou (bool): o consumidor excedeu TIMEOUT em algum acquire.
        onde (str): semaforo em que o consumidor ficou bloqueado.
    """

    def __init__(self):
        """Inicializa o buffer e os semaforos."""
        self.buffer = [None] * N
        self.vazio = threading.Semaphore(N)
        self.cheio = threading.Semaphore(0)
        self.mutex = threading.Semaphore(1)
        self.recebidas = []
        self.produzidas = 0
        self.travou = False
        self.onde = ""


def produtor(est):
    """
    Thread do sensor com a ordem de aquisicao invertida.

    Parametros:
        est (Estado): estado compartilhado.

    Retorno:
        None. Nao retorna se ocorrer deadlock.
    """
    entrada = 0
    for amostra in range(TOTAL):
        est.mutex.acquire()               # ordem trocada: mutex antes de vazio
        est.vazio.acquire()               # com o buffer cheio, bloqueia segurando o mutex
        est.buffer[entrada] = amostra
        time.sleep(0)
        entrada = (entrada + 1) % N
        est.produzidas += 1
        est.mutex.release()
        est.cheio.release()


def consumidor(est):
    """
    Thread do motor, igual a da versao 2, registrando onde bloqueou.

    Parametros:
        est (Estado): estado compartilhado.

    Retorno:
        None. O resultado fica em est.recebidas, est.travou e est.onde.
    """
    saida = 0
    for _ in range(TOTAL):
        if not est.cheio.acquire(timeout=TIMEOUT):
            est.travou, est.onde = True, "cheio"
            return
        if not est.mutex.acquire(timeout=TIMEOUT):
            est.cheio.release()           # devolve o permit ja adquirido
            est.travou, est.onde = True, "mutex"
            return
        est.recebidas.append(est.buffer[saida])
        time.sleep(0)
        saida = (saida + 1) % N
        est.mutex.release()
        est.vazio.release()


def executar(numero):
    """
    Executa uma rodada da versao 3 e imprime o resultado.

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
    tp.join(timeout=0.5)
    tempo = time.monotonic() - inicio
    stats = analisar(est.recebidas)
    detalhe = ""
    if est.travou:
        # O timeout so indica falta de progresso. O deadlock e confirmado
        # se, depois do timeout, o produtor continua vivo, sem produzir,
        # e o mutex segue ocupado.
        antes = est.produzidas
        time.sleep(0.2)
        mutex_livre = est.mutex.acquire(blocking=False)
        if mutex_livre:
            est.mutex.release()
        if tp.is_alive() and est.produzidas == antes and not mutex_livre:
            detalhe = (f"(deadlock confirmado: consumidor preso em {est.onde}, "
                       f"produtor preso em vazio segurando o mutex depois de "
                       f"{est.produzidas} amostras)")
        else:
            detalhe = "(timeout sem deadlock confirmado)"
    imprimir_execucao(3, numero, stats, est.travou, tempo, detalhe)
    return stats, est.travou


def main():
    """Executa as EXECUCOES rodadas da versao 3."""
    cabecalho(3, "semaforos com wait(mutex) antes de wait(vazio)")
    for i in range(1, EXECUCOES + 1):
        executar(i)


if __name__ == "__main__":
    main()
