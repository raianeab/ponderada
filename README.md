# Ponderada CC08 - Tato

**Aluna:** Raiane Araujo Brandão (D1 = 6, D2 = 9, N = 7)

Ponderada de Computação CC08 aplicando arquitetura, memória, pipeline, processos/threads, semáforos e deadlock à pulseira sensorial Tato.

O texto da entrega está em [`ponderada/ponderada-tato.md`](ponderada/ponderada-tato.md).

## Como rodar a questão A4

Precisa só de Python 3 (sem bibliotecas extras). Entre na pasta do código:

```bash
cd ponderada/codigo
```

Cada comando roda a versão 3 vezes com 20.000 amostras e imprime consumidas, perdidas, duplicadas e se travou:

```bash
python3 versao1.py   # sem sincronização (demora ~1 min por execução por causa da espera ocupada)
python3 versao2.py   # com semáforos vazio/cheio/mutex
python3 versao3.py   # semáforos com a ordem trocada (trava de propósito)
```
