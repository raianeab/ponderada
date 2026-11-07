"""
comum.py - parametros e funcoes compartilhadas pelas tres versoes da A4.

Ponderada CC08 (Tato) - Raiane Araujo Brandao
D1 = 6, D2 = 9, N = 3 + (9 mod 5) = 7
"""

import sys

N = 7                # tamanho do buffer circular
TOTAL = 20_000       # amostras geradas por execucao
TIMEOUT = 1.0        # segundos sem receber nada para considerar travamento
EXECUCOES = 3


def analisar(recebidas, total=TOTAL):
    """
    Calcula as metricas de uma execucao a partir das amostras recebidas.

    Parametros:
        recebidas (list[int]): numeros das amostras, na ordem de chegada.
        total (int): quantas amostras o produtor deveria entregar.

    Retorno:
        dict com 'consumidas', 'perdidas', 'duplicadas' e 'fora_ordem'.

    Funcionamento:
        As amostras distintas sao obtidas com um conjunto. Na versao 1, o
        consumidor pode ler uma posicao do buffer ainda nao preenchida
        (None); essa leitura conta como consumida, mas nao como amostra
        distinta, e fica fora da comparacao de ordem. 'fora_ordem' conta
        as transicoes em que uma amostra valida e menor que a valida
        anterior (nao o numero de amostras em posicao errada).
    """
    validas = [x for x in recebidas if isinstance(x, int)]
    unicas = set(x for x in validas if 0 <= x < total)
    consumidas = len(recebidas)
    fora_ordem = sum(1 for a, b in zip(validas, validas[1:]) if b < a)
    return {
        "fora_ordem": fora_ordem,
        "consumidas": consumidas,
        "perdidas": total - len(unicas),
        "duplicadas": consumidas - len(unicas),
    }


def imprimir_execucao(versao, numero, stats, travou, tempo, detalhe=""):
    """
    Imprime o resumo de uma execucao em uma linha.

    Parametros:
        versao (int), numero (int): identificam a versao e a execucao.
        stats (dict): resultado de analisar().
        travou (bool): se houve travamento.
        tempo (float): duracao em segundos.
        detalhe (str): informacao adicional opcional.

    Retorno:
        None.
    """
    print(
        f"V{versao} exec {numero} | consumidas={stats['consumidas']:>6} "
        f"| perdidas={stats['perdidas']:>5} | duplicadas={stats['duplicadas']:>5} "
        f"| fora de ordem={stats['fora_ordem']:>5} "
        f"| travou={'SIM' if travou else 'nao'} | tempo={tempo:5.2f}s {detalhe}"
    )
    sys.stdout.flush()


def cabecalho(versao, descricao):
    """
    Imprime o cabecalho de uma versao com os parametros do experimento.

    Parametros:
        versao (int): numero da versao.
        descricao (str): descricao curta da versao.

    Retorno:
        None.
    """
    print(f"=== A4 - Versao {versao}: {descricao} ===")
    print(f"N = {N} | amostras = {TOTAL} | timeout = {TIMEOUT}s | execucoes = {EXECUCOES}")
    print("-" * 95)
