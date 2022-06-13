class Rede:
    def __init__(self):
        self.nodos = []
        self.ip = str
        self.roteadores = []

    def check_nodo(self, nodo):
        for x in self.nodos:
            if x.nome == nodo.nome:
                return True
        return False

    def add_nodo(self, nodo):
        if not self.check_nodo(nodo):
            self.nodos.append(nodo)
