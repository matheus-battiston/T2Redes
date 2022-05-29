class Node:
    def __init__(self, dados):
        ip_prefixo = dados[2].split('/')
        self.nome = dados[0]
        self.mac = dados[1]
        self.ip = ip_prefixo[0]
        self.prefixo = ip_prefixo[1]
        self.gateway = dados[3]

    def receive_arp_request(self, ip_destino):
        if ip_destino in self.ip:
            return True

        return False
