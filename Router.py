from Node import Node
from Funcs import get_ip_rede


class Router:
    def __init__(self, dados):
        self.nome = dados.pop(0)
        self.num_portas = dados.pop(0)
        self.mac = []
        self.ip = []
        self.arp_table = []
        self.router_table = None
        self.redes = []

        for x in range(0, len(dados)):
            if x % 2 == 0:
                self.mac.append(dados[x])
            else:
                self.ip.append(dados[x])

    def get_caminho(self, destino):
        return self.router_table.get_caminho(destino)

    def get_ip_porta(self, ip):
        for x in self.ip:
            if x.split('/')[0].split('.')[0:3] == ip.split('.')[0:3]:
                return x.split('/')[0]

    def eh_local(self, destino):
        for x in self.ip:
            if get_ip_rede(x) == get_ip_rede(destino.ip):
                return True

        return False

    def check_arp_request(self, arp_request):
        for g in self.ip:
            if g.split('/')[0] == arp_request:
                return True

        return False

    def get_roteador_routertable(self, destino):
        for x in self.router_table:
            if destino.gateway.split('.')[:3] == x.net_dest.split('.')[:3]:
                return x.nexthop

    def get_roteador(self, ip):
        for r in self.redes:
            for rot in r.roteadores:
                for ips in rot.ip:
                    if ips.split('/')[0] == ip:
                        return rot

    def get_ip_and_mac(self, ip):
        for count, x in enumerate(self.ip):
            if ip in x:
                return self.mac[count], self.ip[count].split('/')[0]
        return False

    def check_arp_table(self, destino):
        for device in self.arp_table:
            if type(destino) != str:
                if destino.ip == device[0]:
                    return True
            elif destino == device[0]:
                return True

        return False

    def recebe_pacote(self, tipo_do_pacote, quem_enviou, arp_request=None, origemComando=None, destinoComando=None,
                      para_quem=None, mac=None, ip=None, ttl=None):
        if tipo_do_pacote == 'arp_request':
            self.receber_arp_request(quem_enviou, arp_request, mac, ip)
        elif tipo_do_pacote == 'echo_request':
            self.receber_echo_request(quem_enviou, para_quem, origemComando, destinoComando, ttl)
        elif tipo_do_pacote == 'echo_reply':
            self.receber_echo_reply(quem_enviou, origemComando, destinoComando, para_quem, ttl)
        elif tipo_do_pacote == 'arp_reply':
            self.receber_arp_reply(quem_enviou, mac)
        elif tipo_do_pacote == 'time':
            self.receber_time_exceeded(destinoComando, origemComando, ttl)

    def receber_time_exceeded(self, destino, origem, ttl):
        ttl -= 1
        if ttl == 0:
            return
        elif self.eh_local(destino):
            saida = self.get_ip_porta(destino.ip)
            rot = self.get_ip_porta(saida)
            mac, ip = self.get_ip_and_mac(rot)
            if not self.check_arp_table(destino):
                self.enviar_pacote('arp_request', arp_request=destino.ip, quem_enviou=saida)
            if self.check_arp_table(destino):
                self.enviar_pacote('time', para_quem=destino, origemComando=ip, destinoComando=destino,
                                   ttl=ttl)
        else:
            saida = self.get_caminho(destino.ip)
            rot = self.get_ip_porta(saida)
            mac, ip = self.get_ip_and_mac(rot)
            roteador = self.get_roteador(saida)
            if not self.check_arp_table(saida):
                self.enviar_pacote('arp_request', arp_request=saida, quem_enviou=rot, mac=mac, ip=ip)
            if self.check_arp_table(saida):
                self.enviar_pacote('time', para_quem=roteador, origemComando=ip, destinoComando=destino,
                                   ttl=ttl)

    def receber_arp_reply(self, quem_enviou, mac):
        if type(quem_enviou) == str:
            self.arp_table.append((quem_enviou, mac))
        else:
            self.arp_table.append((quem_enviou.ip, mac))

    def receber_arp_request(self, quem_enviou, arp_request, mac, ip):
        # Função de um roteador receber um arp request, recebe o nodo da
        # origem do quest e o ip do gateway
        if self.check_arp_request(arp_request):
            self.arp_table.append((ip, mac))
            mac = self.get_ip_and_mac(arp_request)
            self.enviar_pacote('arp_reply', quem_enviou, mac=mac, arp_request=arp_request)

    def receber_echo_request(self, quem_enviou, para_quem, origem, destino, ttl):

        ttl -= 1
        if ttl == 0:
            ttl = 8
            aux = origem
            origem = destino
            destino = aux
            if self.eh_local(destino):
                saida = self.get_ip_porta(destino.ip)
                if saida is None:
                    saida = self.get_roteador_routertable(destino)

                rot = self.get_ip_porta(saida)
                mac, ip = self.get_ip_and_mac(rot)
                if not self.check_arp_table(destino):
                    self.enviar_pacote('arp_request', arp_request=destino.ip, quem_enviou=saida)
                if self.check_arp_table(destino):
                    self.enviar_pacote('time', para_quem=destino, origemComando=ip, destinoComando=destino,
                                       ttl=ttl)
            else:
                saida = self.get_caminho(destino.ip)
                rot = self.get_ip_porta(saida)
                mac, ip = self.get_ip_and_mac(rot)
                roteador = self.get_roteador(saida)

                if not self.check_arp_table(saida):
                    self.enviar_pacote('arp_request', arp_request=saida, quem_enviou=rot, mac=mac, ip=ip)
                if self.check_arp_table(saida):
                    self.enviar_pacote('time', para_quem=roteador, origemComando=ip, destinoComando=destino,
                                       ttl=ttl)

        elif self.eh_local(destino):
            saida = self.get_ip_porta(destino.ip)
            if not self.check_arp_table(destino):
                self.enviar_pacote('arp_request', arp_request=destino.ip, quem_enviou=saida)
            if self.check_arp_table(destino):
                self.enviar_pacote('echo_request', para_quem=destino, origemComando=origem, destinoComando=destino,
                                   quem_enviou=quem_enviou, ttl=ttl)
        else:
            saida = self.get_caminho(destino.ip)
            rot = self.get_ip_porta(saida)
            mac, ip = self.get_ip_and_mac(rot)
            roteador = self.get_roteador(saida)
            if not self.check_arp_table(saida):
                self.enviar_pacote('arp_request', arp_request=saida, quem_enviou=rot, mac=mac, ip=ip)
            if self.check_arp_table(saida):
                self.enviar_pacote('echo_request', para_quem=roteador, origemComando=origem, destinoComando=destino,
                                   ttl=ttl)

    def receber_echo_reply(self, quem_enviou, origem, destino, para_quem, ttl):

        ttl -= 1
        if ttl == 0:
            ttl = 8
            aux = origem
            origem = destino
            destino = aux
            if self.eh_local(destino):
                saida = self.get_ip_porta(destino.ip)
                if not self.check_arp_table(destino):
                    self.enviar_pacote('arp_request', arp_request=destino.ip, quem_enviou=saida)
                if self.check_arp_table(destino):
                    self.enviar_pacote('time', para_quem=destino, origemComando=origem, destinoComando=destino,
                                       ttl=ttl)
            else:
                saida = self.get_caminho(destino.ip)
                rot = self.get_ip_porta(saida)
                mac, ip = self.get_ip_and_mac(rot)
                roteador = self.get_roteador(saida)
                if not self.check_arp_table(saida):
                    self.enviar_pacote('arp_request', arp_request=saida, quem_enviou=rot, mac=mac, ip=ip)
                if self.check_arp_table(saida):
                    self.enviar_pacote('time', para_quem=roteador, origemComando=ip, destinoComando=destino,
                                       ttl=ttl)
        elif self.eh_local(destino):
            saida = self.get_ip_porta(destino.ip)
            if not self.check_arp_table(destino):
                self.enviar_pacote('arp_request', arp_request=destino.ip, quem_enviou=saida)
            if self.check_arp_table(destino):
                self.enviar_pacote('echo_reply', para_quem=destino, origemComando=origem, destinoComando=destino,
                                   quem_enviou=quem_enviou, ttl=ttl)
        else:
            saida = self.get_caminho(destino.ip)
            rot = self.get_ip_porta(saida)
            mac, ip = self.get_ip_and_mac(rot)
            roteador = self.get_roteador(saida)
            if not self.check_arp_table(saida):
                self.enviar_pacote('arp_request', arp_request=saida, quem_enviou=rot, mac=mac, ip=ip)
            if self.check_arp_table(saida):
                self.enviar_pacote('echo_reply', para_quem=roteador, origemComando=origem, destinoComando=destino,
                                   ttl=ttl)

    def enviar_pacote(self, tipo_do_pacote, para_quem=None, arp_request=None, origemComando=None, destinoComando=None,
                      quem_enviou=None, mac=None, ip=None, ttl=None):
        if tipo_do_pacote == 'arp_request':
            self.enviar_arp_request(arp_request, quem_enviou, mac, ip)
        elif tipo_do_pacote == 'echo_request':
            self.enviar_echo_request(para_quem, origemComando, destinoComando, quem_enviou, ttl)
        elif tipo_do_pacote == 'echo_reply':
            self.enviar_echo_reply(para_quem, origemComando, destinoComando, ttl)
        elif tipo_do_pacote == 'arp_reply':
            self.enviar_arp_reply(para_quem, arp_request, mac)
        elif tipo_do_pacote == 'time':
            self.enviar_time_exceeded(para_quem, origemComando, destinoComando, ttl)

    def enviar_time_exceeded(self, para_quem, origem, destino, ttl):
        if ttl == None:
            ttl = 8
        self.print_time_exeeded(self.nome, para_quem.nome, origem, destino.ip, ttl)
        para_quem.recebe_pacote('time', quem_enviou=self, origemComando=origem, destinoComando=destino, ttl=ttl)

    def enviar_arp_request(self, destino, quem_enviou, mac, ip):
        self.print_arq_request(destino, quem_enviou)
        enviados = []
        for r in self.redes:
            for rot in r.roteadores:
                if rot not in enviados:
                    rot.recebe_pacote('arp_request', quem_enviou=self, para_quem=rot, arp_request=destino, mac=mac,
                                      ip=ip)
                    enviados.append(rot)
            for nod in r.nodos:
                nod.recebe_pacote('arp_request', quem_enviou=self, para_quem=nod, arp_request=destino)

    def enviar_echo_request(self, para_quem, origem, destino, quem_enviou, ttl):
        self.print_echo_request(self.nome, para_quem.nome, origem.ip, destino.ip, ttl)
        para_quem.recebe_pacote('echo_request', quem_enviou=self, para_quem=destino, origemComando=origem,
                                destinoComando=destino, ttl=ttl)

    def enviar_echo_reply(self, para_quem, origem, destino, ttl):
        self.print_echo_reply(self.nome, para_quem.nome, origem.ip, destino.ip, ttl)
        para_quem.recebe_pacote('echo_reply', origemComando=origem, destinoComando=destino, quem_enviou=self, ttl=ttl)

    def enviar_arp_reply(self, destino, arp_request=None, mac=None):
        if isinstance(destino, Node):
            mac, ip = self.get_ip_and_mac(destino.gateway)
            self.print_arp_reply(destino.nome, destino.gateway, mac)
            destino.recebe_pacote('arp_reply', mac=mac, quem_enviou=ip)
        else:
            mac, ip = self.get_ip_and_mac(arp_request)
            self.print_arp_reply(destino.nome, arp_request, mac)
            destino.recebe_pacote('arp_reply', mac=mac, quem_enviou=ip)

    def print_arq_request(self, destino_ip, ip_porta):
        print(f"Note over {self.nome} : ARP Request<br> Who has {destino_ip}? Tell {ip_porta}")

    def print_arp_reply(self, dst_name, src_ip, src_mac):
        print(f"{self.nome} ->> {dst_name} : ARP Reply<br>/{src_ip} is at {src_mac}")

    def print_echo_request(self, src_name, dst_name, src_ip, dst_ip, ttl):
        print(f"{src_name} ->> {dst_name} : ICMP Echo Request<br/>src={src_ip} dst={dst_ip} ttl={ttl}")

    def print_echo_reply(self, src_name, dst_name, src_ip, dst_ip, ttl):
        print(f"{src_name} ->> {dst_name} : ICMP Echo Reply<br/>src={src_ip} dst={dst_ip} ttl={ttl} ")

    def print_time_exeeded(self, src_name, dst_name, src_ip, dst_ip, ttl):
        print(f"{src_name} ->> {dst_name} : ICMP Time Exceeded<br/>src={src_ip} dst={dst_ip} ttl={ttl}")
