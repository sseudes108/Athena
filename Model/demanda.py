from itertools import accumulate  # Importa a função accumulate para calcular somatórios progressivos

class Demanda():
    def __init__(self):
        # Inicializa a lista de demanda com 24 valores (um para cada hora do dia), todos zerados
        self.demanda = [0] * 24
    
    # Define a demanda manualmente
    def set_demanda(self, demanda):
        self.demanda = demanda

    # Retorna a demanda atual
    def get_demanda(self):
        return self.demanda
    
class DemandaAtual(Demanda):
    def __init__(self):
        super().__init__()  # Herda a estrutura da classe Demanda

class DemandaAcumulada(Demanda):
    def __init__(self):
        super().__init__()

    # Recalcula a demanda acumulada a partir de uma derivação (diferenças por hora)
    def recalcular_acumulo(self, derivacao):
        acumulo = list(accumulate(derivacao))  # Soma progressiva
        self.set_demanda(acumulo)  # Armazena como nova demanda

class CapacidadeOperacional(Demanda):
    def __init__(self):
        super().__init__()

    # Define a capacidade de produção (igual a set_demanda mas com nome semântico)
    def set_capacidade_producao(self, capacidade):
        self.demanda = capacidade

    # Retorna a capacidade de produção
    def get_capacidade_producao(self):
        return self.demanda