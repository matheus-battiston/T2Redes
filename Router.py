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

    def ip_saida(self, destino):  # Retorna o ip para a saída de um pacote do roteador
        rede_destino = get_ip_rede(destino.ip)
        porta = self.router_table.get_n_porta(rede_destino)
        saida = self.get_ip_porta(porta)
        return saida

    def prepara_time_local(self, destino, origem, ttl):  # Prepara o envio de um time exceeded quando deve ser enviado
        # para alguém na mesma rede
        saida = self.ip_saida(destino)
        if not self.check_arp_table(destino):
            self.enviar_pacote('arp_request', arp_request=destino.ip, quem_enviou=saida)
        if self.check_arp_table(destino):
            self.enviar_pacote('time', para_quem=destino, origemComando=origem, destinoComando=destino,
                               ttl=ttl)

    def prepara_time_longe(self, destino, origem, ttl):  # Prepara o envio de um time exceeded quando não é feito
        # na mesma rede. Chama a função para fazer o encaminhamento
        ip, mac, rot, roteador, saida = self.dados_nao_eh_local(destino)
        if not self.check_arp_table(saida):
            self.enviar_pacote('arp_request', arp_request=saida, quem_enviou=rot, mac=mac, ip=ip)
        if self.check_arp_table(saida):
            self.enviar_pacote('time', para_quem=roteador, origemComando=origem, destinoComando=destino,
                               ttl=ttl)

    def prepara_echo_longe(self, comando, origem, destino, ttl):  # Prepara o envio de um comando echo(reply ou request)
        # quando não é enviado na mesma rede
        ip, mac, rot, roteador, saida = self.dados_nao_eh_local(destino)
        if not self.check_arp_table(saida):
            self.enviar_pacote('arp_request', arp_request=saida, quem_enviou=rot, mac=mac, ip=ip)
        if self.check_arp_table(saida):
            self.enviar_pacote(comando, para_quem=roteador, origemComando=origem, destinoComando=destino,
                               ttl=ttl)

    def prepara_echo_local(self, comando, origem, destino, ttl):  # Prepara o envio de um comando echo (reply ou
        # request) quando não é enviado na mesma rede
        saida = self.ip_saida(destino)
        if not self.check_arp_table(destino):
            self.enviar_pacote('arp_request', arp_request=destino.ip, quem_enviou=saida)
        if self.check_arp_table(destino):
            self.enviar_pacote(comando, para_quem=destino, origemComando=origem, destinoComando=destino,
                               ttl=ttl)

    def dados_nao_eh_local(self, destino):  # Chama funções para realizar o encaminhamento correto
        saida = self.get_caminho(destino.ip)
        porta = self.router_table.get_n_porta(saida)
        rot = self.get_ip_porta(porta)
        mac, ip = self.get_ip_and_mac(rot)
        roteador = self.get_roteador(saida)
        return ip, mac, rot, roteador, saida

    def get_caminho(self, destino):  # Chama o router table para retornar o nexthop adequado para esse destino
        return self.router_table.get_caminho(destino)

    def get_ip_porta(self, n_porta):  # Recebe o número de uma porta e retorna seu IP
        return self.ip[int(n_porta)]

    def eh_local(self, destino):  # Checa se um nodo está na mesma rede deste nodo
        for x in self.ip:
            if get_ip_rede(x) == get_ip_rede(destino.ip):
                return True

        return False

    def check_arp_request(self, arp_request):  # Checa se deve responder o arp request
        for g in self.ip:
            if g.split('/')[0] == arp_request:
                return True

        return False

    def get_roteador(self, ip):  # Recebe um ip e dentro dos roteadores alcançaveis retorna o objeto com ip
        # correspondente
        for r in self.redes:
            for rot in r.roteadores:
                for ips in rot.ip:
                    if ips.split('/')[0] == ip:
                        return rot

    def get_ip_and_mac(self, ip):  # Perecorre a lista de portas de um roteador, quando encontrado o que queremos
        # retorna o mac e o ip
        for count, x in enumerate(self.ip):
            if ip in x:
                return self.mac[count], self.ip[count].split('/')[0]
        return False

    def check_arp_table(self, destino):  # Faz a checagem na arp table se existe um ip adicionado
        for device in self.arp_table:
            if type(destino) != str:
                if destino.ip == device[0]:
                    return True
            elif destino == device[0]:
                return True

        return False

    def recebe_pacote(self, tipo_do_pacote, quem_enviou, arp_request=None, origemComando=None, destinoComando=None,
                      para_quem=None, mac=None, ip=None, ttl=None):  # Função feita para implementar o recebimento de
        # um pacote, identifica o tipo dele e envia para a função especifica de cada tipo

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

    def receber_time_exceeded(self, destino, origem, ttl):  # Função que recebe um time exceeded. Checa se o destino
        # está na mesma rede e chama a função que fará o encaminhamento
        ttl -= 1
        if ttl == 0:
            return
        elif self.eh_local(destino):
            self.prepara_time_local(destino, origem, ttl)
        else:
            self.prepara_time_longe(destino, origem, ttl)

    def receber_arp_reply(self, quem_enviou, mac):  # Apenas realiza a adição no arp table
        if type(quem_enviou) == str:
            self.arp_table.append((quem_enviou, mac))
        else:
            self.arp_table.append((quem_enviou.ip, mac))

    def receber_arp_request(self, quem_enviou, arp_request, mac, ip):
        # Função de um roteador receber um arp request, recebe o nodo da
        # origem do quest e o ip do gateway
        if self.check_arp_request(arp_request):
            self.arp_table.append((ip, mac))
            self.enviar_pacote('arp_reply', quem_enviou, arp_request=arp_request)

    def receber_echo_request(self, quem_enviou, para_quem, origem, destino, ttl):  # Recebimento do echo request.
        # Faz o decremento do ttl e define se deve ser o echo request deve ser encaminhado ou enviado um time exceeded.
        # Chama as funções para encaminhar nos dois casos
        ttl -= 1
        if ttl == 0:
            ttl = 8
            destino = origem
            if self.eh_local(destino):
                ip = self.ip_saida(destino)
                self.prepara_time_local(origem, ip, ttl)
            else:
                ip = self.dados_nao_eh_local(destino)[0]
                self.prepara_time_longe(origem, ip, ttl)

        elif self.eh_local(destino):
            self.prepara_echo_local('echo_request', origem, destino, ttl)
        else:
            self.prepara_echo_longe('echo_request', origem, destino, ttl)

    def receber_echo_reply(self, quem_enviou, origem, destino, para_quem, ttl):  # Igual recebimento de echo request

        ttl -= 1
        if ttl == 0:
            ttl = 8
            destino = origem
            if self.eh_local(destino):
                ip = self.ip_saida(destino)
                self.prepara_time_local(origem, ip, ttl)
            else:
                ip = self.dados_nao_eh_local(destino)[0]
                self.prepara_time_longe(origem, ip, ttl)

        elif self.eh_local(destino):
            self.prepara_echo_local('echo_reply', origem, destino, ttl)

        else:
            self.prepara_echo_longe('echo_reply', origem, destino, ttl)

    def enviar_pacote(self, tipo_do_pacote, para_quem=None, arp_request=None, origemComando=None, destinoComando=None,
                      quem_enviou=None, mac=None, ip=None, ttl=None):  # Função responsável por enviar um pacote.
        # Faz a checagem do tipo do pacote e chama as funções de envio correspondente
        if tipo_do_pacote == 'arp_request':
            self.enviar_arp_request(arp_request, quem_enviou, mac, ip)
        elif tipo_do_pacote == 'echo_request':
            self.enviar_echo_request(para_quem, origemComando, destinoComando, ttl)
        elif tipo_do_pacote == 'echo_reply':
            self.enviar_echo_reply(para_quem, origemComando, destinoComando, ttl)
        elif tipo_do_pacote == 'arp_reply':
            self.enviar_arp_reply(para_quem, arp_request, mac)
        elif tipo_do_pacote == 'time':
            self.enviar_time_exceeded(para_quem, origemComando, destinoComando, ttl)

    def enviar_time_exceeded(self, para_quem, origem, destino, ttl):  # Função de envio do time exceeded.
        # Faz o print e chama a função de receber pacote de para quem deve ser enviado (Identificado em para_quem)
        if ttl is None:
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

    def enviar_echo_request(self, para_quem, origem, destino, ttl): # Função de envio do echo_request.
        # Faz o print e chama a função de receber pacote de para quem deve ser enviado (Identificado em para_quem)
        self.print_echo_request(self.nome, para_quem.nome, origem.ip, destino.ip, ttl)
        para_quem.recebe_pacote('echo_request', quem_enviou=self, para_quem=destino, origemComando=origem,
                                destinoComando=destino, ttl=ttl)

    def enviar_echo_reply(self, para_quem, origem, destino, ttl):
        # Função de envio do echo_reply.
        # Faz o print e chama a função de receber pacote de para quem deve ser enviado (Identificado em para_quem)
        self.print_echo_reply(self.nome, para_quem.nome, origem.ip, destino.ip, ttl)
        para_quem.recebe_pacote('echo_reply', origemComando=origem, destinoComando=destino, quem_enviou=self, ttl=ttl,
                                para_quem=destino)

    def enviar_arp_reply(self, destino, arp_request=None, mac=None):
        # Função de envio do arp_reply.
        if isinstance(destino, Node):
            mac, ip = self.get_ip_and_mac(destino.gateway)
            self.print_arp_reply(destino.nome, destino.gateway, mac)
            destino.recebe_pacote('arp_reply', mac=mac, quem_enviou=ip)
        else:
            mac, ip = self.get_ip_and_mac(arp_request)
            self.print_arp_reply(destino.nome, arp_request, mac)
            destino.recebe_pacote('arp_reply', mac=mac, quem_enviou=ip)

    def print_arq_request(self, destino_ip, ip_porta):
        destino_ip = destino_ip.split('/')[0]
        ip_porta = ip_porta.split('/')[0]
        print(f"Note over {self.nome} : ARP Request<br/>Who has {destino_ip}? Tell {ip_porta}")

    def print_arp_reply(self, dst_name, src_ip, src_mac):
        src_ip = src_ip.split('/')[0]
        print(f"{self.nome} ->> {dst_name} : ARP Reply<br/>{src_ip} is at {src_mac}")

    def print_echo_request(self, src_name, dst_name, src_ip, dst_ip, ttl):
        src_ip = src_ip.split('/')[0]
        dst_ip = dst_ip.split('/')[0]
        print(f"{src_name} ->> {dst_name} : ICMP Echo Request<br/>src={src_ip} dst={dst_ip} ttl={ttl}")

    def print_echo_reply(self, src_name, dst_name, src_ip, dst_ip, ttl):
        src_ip = src_ip.split('/')[0]
        dst_ip = dst_ip.split('/')[0]
        print(f"{src_name} ->> {dst_name} : ICMP Echo Reply<br/>src={src_ip} dst={dst_ip} ttl={ttl}")

    def print_time_exeeded(self, src_name, dst_name, src_ip, dst_ip, ttl):
        src_ip = src_ip.split('/')[0]
        dst_ip = dst_ip.split('/')[0]
        print(f"{src_name} ->> {dst_name} : ICMP Time Exceeded<br/>src={src_ip} dst={dst_ip} ttl={ttl}")
