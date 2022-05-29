import os
import sys
from Node import *
from Router import *


def leitor(nome_arquivo):  # Le o arquivo e retorna uma lista em que cada posição é uma linha
    linhas = []
    diretorio = os.getcwd() + '/Arquivos/' + nome_arquivo
    arquivo = open(diretorio, 'r')

    for line in arquivo:
        linhas.append(line.replace('\n', '').split(','))
    arquivo.close()

    return linhas


def cadastrar_nodos(topologia):  # Cria uma lista de objetos NODO, percorre a lista até encontrar o começo da descrição
    # de routers
    nodos_cadastrados = []
    for nodos in topologia[1:]:
        if nodos[0] == '#ROUTER':
            break
        nodos_cadastrados.append(Node(nodos))
    return nodos_cadastrados


def cadastrar_roteadores(topologia):  # Cria uma lista de objetos ROTEADOR, percorre a lista até encontrar o começo da
    # descrição de routertable
    roteadores_cadastrados = []
    for roteadores in topologia:
        if roteadores[0] == '#ROUTERTABLE':
            break
        roteadores_cadastrados.append(Router(roteadores))

    return roteadores_cadastrados

def print_arq_request(nodo, origem, destino):
    print(f"Note over {nodo} : ARP Request<br> Who has {destino}? Tell {origem})")


def executa_ping(nodos, roteadores, origem, destino):
    pass

def executa_tracerout(nodos, roteadores, origem, destino):
    pass


if __name__ == '__main__':
    argumentos = sys.argv[1:]
    descricao_topologia = leitor(argumentos[0])
    comando = argumentos[1]
    origem = argumentos[2]
    destino = argumentos[3]
    Nodos = cadastrar_nodos(descricao_topologia)
    Roteadores = cadastrar_roteadores(descricao_topologia[len(Nodos) + 2:])

    if comando.lower() == 'ping':
        executa_ping(Nodos, Roteadores, origem, destino)
    elif comando.lower() == 'tracerout':
        executa_tracerout(Nodos, Roteadores, origem, destino)
    else:
        print("Comando invalido")
