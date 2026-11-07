"""
versao1.py - A4 versao 1: buffer circular sem sincronizacao.

Ponderada CC08 (Tato) - Raiane Araujo Brandao (N = 7)

Produtor (sensor) e consumidor (motor) compartilham o buffer e um contador
de posicoes ocupadas, sem semaforo nem lock, e usam espera ocupada. O
time.sleep(0) entre ler e escrever o contador simula uma interrupcao no
pior momento e torna a condicao de corrida visivel.

Como rodar:  python3 versao1.py
"""

import threading
import time

from comum import N, TOTAL, TIMEOUT, EXECUCOES, analisar, imprimir_execucao, cabecalho

LIMITE = 300.0   # segundos; uma execucao normal leva cerca de 60 s


class Estado:
    """
    Estado compartilhado de uma execucao.

    Atributos:
        buffer (list): buffer circular de N posicoes.
        contador (int): posicoes ocupadas, sem nenhuma protecao.
        recebidas (list[int]): amostras lidas pelo consumidor.
        produtor_terminou (bool): o produtor ja gerou todas as amostras.
        parar (bool): avisa o produtor para desistir apos um travamento.
        travou (bool): o consumidor detectou travamento.
    """

    def __init__(self):
        """Inicializa o estado vazio."""
        self.buffer = [None] * N
        self.contador = 0
        self.recebidas = []
        self.produtor_terminou = False
        self.parar = False
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
        while est.contador >= N:          # espera ocupada: buffer cheio
            if est.parar:
                return
        est.buffer[entrada] = amostra
        entrada = (entrada + 1) % N
        # Leitura e escrita do contador separadas de proposito: a outra
        # thread pode atualizar o contador nesse intervalo e o valor dela
        # e sobrescrito (atualizacao perdida).
        tmp = est.contador
        time.sleep(0)
        est.contador = tmp + 1
    est.produtor_terminou = True


def consumidor(est):
    """
    Thread do motor: retira amostras do buffer e registra o que recebeu.

    Parametros:
        est (Estado): estado compartilhado.

    Retorno:
        None. O resultado fica em est.recebidas e est.travou.

    Funcionamento:
        Termina normalmente quando o produtor acabou e o contador indica
        buffer vazio. Se ficar TIMEOUT segundos sem receber nada com o
        produtor ainda ativo, registra travamento.
    """
    saida = 0
    ultimo = time.monotonic()
    while True:
        while est.contador <= 0:          # espera ocupada: buffer vazio
            if est.produtor_terminou:
                return
            if time.monotonic() - ultimo > TIMEOUT:
                est.travou = True
                est.parar = True
                return
        est.recebidas.append(est.buffer[saida])
        saida = (saida + 1) % N
        ultimo = time.monotonic()
        tmp = est.contador                # mesma janela de corrida do produtor
        time.sleep(0)
        est.contador = tmp - 1


def executar(numero):
    """
    Executa uma rodada da versao 1 e imprime o resultado.

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
    # Limite global: se o consumidor nao terminar em LIMITE segundos
    # (algum estado nao previsto da corrida), a execucao e encerrada.
    tc.join(timeout=LIMITE)
    if tc.is_alive():
        est.travou = True
    est.parar = True
    tp.join(timeout=2)
    tempo = time.monotonic() - inicio
    stats = analisar(est.recebidas)
    detalhe = f"(contador final = {est.contador})"
    imprimir_execucao(1, numero, stats, est.travou, tempo, detalhe)
    return stats, est.travou


def main():
    """Executa as EXECUCOES rodadas da versao 1."""
    cabecalho(1, "sem sincronizacao (contador + espera ocupada)")
    for i in range(1, EXECUCOES + 1):
        executar(i)


if __name__ == "__main__":
    main()
