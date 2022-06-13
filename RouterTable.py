class RouterTable:
    def __init__(self, dados):
        self.nome = dados[0]
        self.net_dest = dados[1]
        self.nexthop = dados[2]
        self.porta = dados[3]
