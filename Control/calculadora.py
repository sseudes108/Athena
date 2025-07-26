from itertools import accumulate

import Control.athena as Athena
from Model.demanda import DemandaAtual, DemandaAcumulada, CapacidadeOperacional

class Calculadora():
    def __init__(self):
        pass
    
    def athena(self, tma, demanda_atual, demanda_acumulada, capacidade_operacional):
        print("Athena!")
        return Athena.calcular_capacity(tma, demanda_atual, demanda_acumulada, capacidade_operacional)

    def create_instancias(self):
        demanda_atual = DemandaAtual()
        demanda_acumulada = DemandaAcumulada()
        capacidade_operacional = CapacidadeOperacional()
        
        return demanda_atual, demanda_acumulada, capacidade_operacional
    
    def calcular_acumulo(self, derivacao):
        acumulo = list(accumulate(derivacao))
        return acumulo

def main():
    pass

if __name__ == '__main__':
    main()