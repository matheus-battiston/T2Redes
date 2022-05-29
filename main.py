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


def print_arq_request(nodo, origem_ip, destino_ip):

    print(f"Note over {nodo} : ARP Request<br> Who has {destino_ip}? Tell {origem_ip}")


def print_arq_reply(src_name, dst_name, src_ip, src_mac):
    print(f"{src_name} ->> {dst_name} : ARP Reply<br>/{src_ip} is at {src_mac}")


def print_echo_request(src_name, dst_name, src_ip, dst_ip, ttl):
    print(f"{src_name} ->> {dst_name} : ICMP Echo Request<br/>src={src_ip} dst={dst_ip} ttl={ttl}")


def print_echo_reply(src_name, dst_name, src_ip, dst_ip, ttl):
    print(f"{src_name} ->> {dst_name} : ICMP Echo Reply<br/>src={src_ip} dst={dst_ip} ttl={ttl} ")


def print_time_exeeded(src_name, dst_name, src_ip, dst_ip, ttl):
    print(f"{src_name} ->> {dst_name} : ICMP Time Exceeded<br/>src={src_ip} dst={dst_ip} ttl={ttl}")


def executa_ping(nodos, roteadores):
    nodo_origem = get_nodo(nodos, origem)
    nodo_destino = get_nodo(nodos, destino)

    print_arq_request(origem, nodo_origem.ip, destino)

    for x in nodos:
        if x.receive_arp_request(nodo_destino.ip):
            print_arq_reply(x.nome, origem, nodo_destino.ip, x.mac)


def get_nodo(nodos, nome):
    nodo = None
    for n in nodos:
        if n.nome == nome:
            nodo = n

    return nodo


def executa_tracerout(nodos, roteadores):
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
        executa_ping(Nodos, Roteadores)
    elif comando.lower() == 'tracerout':
        executa_tracerout(Nodos, Roteadores)
    else:
        print("Comando invalido")
