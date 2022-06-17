import os
import sys

import Comando
from Node import Node
from Router import *
from Rede import *
from RouterTable import *
from Funcs import get_ip_rede

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
        novo_nodo = Node(nodos)
        rede = rede_triagem(novo_nodo)
        novo_nodo.minha_rede = rede
        nodos_cadastrados.append(novo_nodo)

    return nodos_cadastrados


def rede_triagem(nodo):
    if isinstance(nodo, Node):
        ip = nodo.ip
        ip = get_ip_rede(ip)
        existe_rede = existe_a_rede(ip)
        if existe_rede is not False:
            existe_rede.nodos.append(nodo)
            return existe_rede
        else:
            cadastra_nova_rede(nodo, ip)
            return Redes[len(Redes) - 1]

    elif isinstance(nodo, Router):
        for n in nodo.ip:
            ip = n
            ip = get_ip_rede(ip)

            existe_rede = existe_a_rede(ip)
            if existe_rede is not False:
                nodo.redes.append(existe_rede)
            else:
                cadastra_nova_rede(nodo, ip)

def cadastra_nova_rede(nodo, ip):
    if isinstance(nodo, Node):
        nova_rede = Rede()
        nova_rede.ip = ip
        nova_rede.nodos.append(nodo)
        Redes.append(nova_rede)
    else:
        nova_rede = Rede()
        nova_rede.ip = ip
        nova_rede.roteadores.append(nodo)
        nodo.redes.append(nova_rede)
        Redes.append(nova_rede)


def existe_a_rede(ip):
    for r in Redes:
        if r.ip == ip:
            return r

    return False


def cadastrar_roteadores(topologia):  # Cria uma lista de objetos ROTEADOR, percorre a lista até encontrar o começo da
    # descrição de routertable
    roteadores_cadastrados = []
    for roteadores in topologia:
        if roteadores[0] == '#ROUTERTABLE':
            break
        roteador_novo = Router(roteadores)
        rede_triagem(roteador_novo)
        adiciona_roteador_a_rede(roteador_novo)
        roteadores_cadastrados.append(roteador_novo)

    return roteadores_cadastrados

def adiciona_roteador_a_rede(roteador_novo):
    aux = '.'
    for r in Redes:
        for entradas in roteador_novo.ip:
            ip = get_ip_rede(entradas)
            if ip in r.ip:
                if roteador_novo not in r.roteadores:
                    r.roteadores.append(roteador_novo)


def router_table(topologia):  # Cadastra nos roteadores os RouterTables descritos na topologia
    for linha in topologia:
        for router in Roteadores:
            if linha[0] == router.nome:
                if router.router_table is None:
                    router.router_table = RouterTable()
                    router.router_table.add_info(linha[1:])
                else:
                    router.router_table.add_info(linha[1:])


def get_rede(ip):
    for r in Redes:
        if r.ip == ip:
            return r


def get_nodo(nodos, nome):  # Função que recebe um nome e retorna o nodo correspondente
    nodo = None
    for n in nodos:
        if n.nome == nome:
            nodo = n

    return nodo


def executa_ping(nodos, roteadores):
    nodo_origem = get_nodo(nodos, origem)
    nodo_destino = get_nodo(nodos, destino)
    rede_origem = nodo_origem.minha_rede

    nodo_origem.ping(nodo_destino, roteadores)


def executa_tracerout(nodos, roteadores):
    nodo_origem = get_nodo(nodos, origem)
    nodo_destino = get_nodo(nodos, destino)
    rede_origem = nodo_origem.minha_rede

    nodo_origem.tracerout(nodo_destino, roteadores)


if __name__ == '__main__':
    argumentos = ['Topologia3.txt', 'traceroute', 'n1', 'n2']
    descricao_topologia = leitor(argumentos[0])
    comando = argumentos[1]
    origem = argumentos[2]
    destino = argumentos[3]
    Redes = []
    Nodos = cadastrar_nodos(descricao_topologia)
    Roteadores = cadastrar_roteadores(descricao_topologia[len(Nodos) + 2:])
    router_table(descricao_topologia[len(Nodos) + len(Roteadores) + 3:])

    Comando.comando = comando.lower()
    if comando.lower() == 'ping':
        executa_ping(Nodos, Roteadores)
    elif comando.lower() == 'traceroute':
        executa_tracerout(Nodos, Roteadores)
    else:
        print("Comando invalido")
