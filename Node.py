import Comando


class Node:
    def __init__(self, dados):
        self.nome = dados[0]
        self.mac = dados[1]
        self.ip = dados[2]
        self.gateway = dados[3]
        self.arp_table = []
        self.minha_rede = None
        self.comando = str
        self.destino = None
        self.roteador = None
        self.ttl_enviado = 0

    def get_router(self, gateway):  # Função para retornar o objeto roteador do gateway padrao
        for r in self.minha_rede.roteadores:
            for g in r.ip:
                if gateway in g:
                    return r
        return False

    def check_same_rede(self, ip_destino):  # Função para identificar se um ip está na mesma rede deste nodo
        for n in self.minha_rede.nodos:
            if n.ip == ip_destino:
                return True

        return False

    def check_arp_table(self, destino):  # Função para checar se um destino está na arp table deste nodo
        for device in self.arp_table:
            if type(destino) != str:
                if destino.ip == device[0]:
                    return True
            elif destino == device[0]:
                return True

        return False

    def enviar_pacote(self, tipo_pacote, para_quem=None, arp_request=None, origemComando=None, destinoComando=None,
                      Roteadores=None):
        if tipo_pacote == 'arp_request':
            self.envia_arp_request(arp_request)
        elif tipo_pacote == 'echo_request':
            self.envia_echo_request(para_quem, origemComando, destinoComando)
        elif tipo_pacote == 'arp_reply':
            self.envia_arp_reply(para_quem)
        elif tipo_pacote == 'echo_reply':
            if self.check_same_rede(destinoComando.ip):
                self.envia_echo_reply(destinoComando, origemComando, destinoComando)
            else:
                z = self.get_router(self.gateway)
                self.envia_echo_reply(z, origemComando, destinoComando)

    def envia_echo_request(self, para_quem, origemComando, destinoComando):  # Envio do echo_request, identifica se é
        # enviado para um nodo ou para o gateway padrao
        if Comando.comando == 'ping':
            ttl = 8
        else:
            ttl = self.ttl_enviado + 1

        if para_quem != self.gateway:
            self.print_echo_request(para_quem.nome, origemComando.ip, destinoComando.ip, ttl)
            para_quem.recebe_pacote('echo_request', origemComando=origemComando,
                                    destinoComando=destinoComando, quem_enviou=self, ttl=ttl)
        else:
            roteador = self.get_router(self.gateway)
            self.print_echo_request(roteador.nome, origemComando.ip, destinoComando.ip, ttl)
            roteador.recebe_pacote('echo_request', origemComando=origemComando,
                                   destinoComando=destinoComando, quem_enviou=self, ttl=ttl)

    def envia_arp_reply(self, destino):
        self.print_arq_reply(destino.nome, destino.ip, self.mac)
        destino.recebe_pacote('arp_reply', mac=self.mac, quem_enviou=self)

    def envia_echo_reply(self, para_quem, origemComando, destinoComando):
        ttl = 8

        self.print_echo_reply(para_quem.nome, origemComando.ip, destinoComando.ip, ttl)
        para_quem.recebe_pacote('echo_reply', self, para_quem=destinoComando, origemComando=origemComando,
                                destinoComando=destinoComando, ttl=ttl)

    def envia_arp_request(self, arp_request):

        if arp_request != self.gateway:
            self.print_arq_request(arp_request.ip)
            for n in self.minha_rede.nodos:
                n.recebe_pacote('arp_request', arp_request=arp_request.ip, quem_enviou=self, mac=self.mac)
        else:
            self.print_arq_request(arp_request)
            roteador = self.get_router(self.gateway)
            roteador.recebe_pacote('arp_request', self, arp_request=arp_request, ip=self.ip, mac=self.mac)

    def recebe_pacote(self, tipo_pacote, arp_request=None, quem_enviou=None, mac=None, origemComando=None,
                      destinoComando=None, para_quem=None, ttl=None):
        if tipo_pacote == 'arp_request':
            self.recebe_arp_request(arp_request, quem_enviou)
        elif tipo_pacote == 'arp_reply':
            self.recebe_arp_reply(quem_enviou, mac)
        elif tipo_pacote == 'echo_request':
            self.recebe_echo_request(origemComando, destinoComando)
        elif tipo_pacote == 'echo_reply':
            self.recebe_echo_reply(para_quem)
        elif tipo_pacote == 'time':
            self.recebe_time_exceeded(destinoComando)

    def recebe_time_exceeded(self, destinoComando):
        self.ttl_enviado += 1
        if destinoComando.nome == self.nome:
            if Comando.comando == 'ping':
                return
            elif Comando.comando == 'traceroute':
                self.tracerout(self.destino, None)


    def recebe_echo_reply(self, destinoComando):
        if destinoComando.nome == self.nome:
            return

    def recebe_echo_request(self, origemComando, destinoComando):
        if destinoComando.nome == self.nome:
            self.enviar_pacote('echo_reply', origemComando=destinoComando, destinoComando=origemComando)

    def recebe_arp_reply(self, quem_enviou, mac):
        self.arp_table.append((quem_enviou, mac))

    def recebe_arp_request(self, arp_request, quem_enviou):
        if arp_request == self.ip:
            self.enviar_pacote('arp_reply', para_quem=quem_enviou)
        return None

    def ping(self, destino, roteadores):  # Função principal para o comando PING
        ttl = self.ttl_enviado + 1
        origem = self
        self.comando = 'ping'
        self.destino = destino
        if self.check_same_rede(destino.ip):
            if self.check_arp_table(destino):
                self.enviar_pacote('echo_request', para_quem=destino, destinoComando=destino, origemComando=self)
            else:
                self.enviar_pacote('arp_request', arp_request=destino, Roteadores=roteadores)
                self.enviar_pacote('echo_request', para_quem=destino, destinoComando=destino, origemComando=self)
        else:
            if self.check_arp_table(self.gateway):
                self.enviar_pacote('echo_request', para_quem=self.gateway, origemComando=self, destinoComando=destino)
            else:
                self.enviar_pacote('arp_request', arp_request=self.gateway)
                self.enviar_pacote('echo_request', para_quem=self.gateway, origemComando=self,
                                   destinoComando=destino)

    def tracerout(self, destino, roteadores):
        self.comando = 'traceroute'
        self.destino = destino
        if self.check_same_rede(destino.ip):
            if self.check_arp_table(destino):
                self.enviar_pacote('echo_request', para_quem=destino, destinoComando=destino, origemComando=self)
            else:
                self.enviar_pacote('arp_request', arp_request=destino)
                self.enviar_pacote('echo_request', para_quem=destino, destinoComando=destino, origemComando=self,
                                   Roteadores=roteadores)
        else:
            envio = self.get_router(self.gateway)

            if self.check_arp_table(self.gateway):
                self.enviar_pacote('echo_request', para_quem=envio, origemComando=self, destinoComando=destino)
            else:
                self.enviar_pacote('arp_request', arp_request=self.gateway)
                self.enviar_pacote('echo_request', para_quem=envio, origemComando=self, destinoComando=destino)

    def print_arq_request(self, destino_ip):
        destino_ip = destino_ip.split('/')[0]
        ip = self.ip.split('/')[0]
        print(f"Note over {self.nome} : ARP Request<br/>Who has {destino_ip}? Tell {ip}")

    def print_arq_reply(self, quem_recebe, destino, src_mac):
        ip = self.ip.split('/')[0]
        print(f"{self.nome} ->> {quem_recebe} : ARP Reply<br/>{ip} is at {src_mac}")

    def print_echo_request(self, quem_recebe, origem, destino, ttl):
        origem = origem.split('/')[0]
        destino = destino.split('/')[0]
        print(f"{self.nome} ->> {quem_recebe} : ICMP Echo Request<br/>src={origem} dst={destino} ttl={ttl}")

    def print_echo_reply(self, quem_recebe, origem, destino, ttl):
        origem = origem.split('/')[0]
        destino = destino.split('/')[0]
        print(f"{self.nome} ->> {quem_recebe} : ICMP Echo Reply<br/>src={origem} dst={destino} ttl={ttl}")

    def print_time_exeeded(self, dst_name, dst_ip, ttl):
        print(f"{self.nome} ->> {dst_name} : ICMP Time Exceeded<br/>src={self.ip} dst={dst_ip} ttl={ttl}")
