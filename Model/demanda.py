class Demanda():
    def __init__(self):
        self.demanda = [0] * 24
    
    def set_demanda(self, demanda): self.demanda = demanda
    def get_demanda(self): return self.demanda
    
class DemandaAtual(Demanda):
    def __init__(self):
        super().__init__()
        
class DemandaAcumulada(Demanda):
    def __init__(self):
        super().__init__()
        
class CapacidadeOperacional(Demanda):
    def __init__(self):
        super().__init__()
        
    def set_capacidade_operacional(self, capacidade): self.demanda = capacidade
    def get_capacidade_operacional(self): return self.demanda