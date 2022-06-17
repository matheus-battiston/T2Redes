from Funcs import get_ip_rede

class RouterTable:
    def __init__(self):
        self.nome = []
        self.net_dest = []
        self.nexthop = []
        self.porta = []

    def add_info(self, info):
        self.net_dest.append(info[0])
        self.nexthop.append(info[1])
        self.porta.append(info[2])

    def get_caminho(self, ip):
        ip_rede = get_ip_rede(ip)
        for enum, x in enumerate(self.net_dest):
            if x.split('/')[0] == ip_rede:
                return self.nexthop[enum]

        for enum, x in enumerate(self.net_dest):
            if x.split('/')[0] == '0.0.0.0':
                return self.nexthop[enum]

