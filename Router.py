class Router:
    def __init__(self, dados):
        self.nome = dados.pop(0)
        self.num_portas = dados.pop(0)
        self.mac = []
        self.ip = []

        for x in range(0, len(dados)):
            if x % 2 == 0:
                self.mac.append(dados[x])
            else:
                self.ip.append(dados[x])
