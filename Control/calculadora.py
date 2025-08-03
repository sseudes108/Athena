# Módulo de orquestração de cálculos de capacidade

import Control.athena as Athena  # Algoritmo principal de cálculo
from Model.demanda import DemandaAcumulada, CapacidadeOperacional  # Modelos de dados

class Calculadora():
    def set_streamlit(self, streamlit):
        self.streamlit = streamlit 
        
    def athena(self):
        """
        Executa o algoritmo Athena para cálculo de capacidade
        
        Parâmetros:
            tma: Tempo Médio de Atendimento (segundos)
            demanda_atual: Instância de DemandaAtual
            demanda_acumulada: Instância de DemandaAcumulada
            capacidade_operacional: Instância de CapacidadeOperacional
        
        Retorna:
            Resultado do cálculo de capacidade (normalmente lista de analistas)
        """
        return Athena.calcular_capacity(self.streamlit.session_state, self)

    def create_instancias(self):
        """
        Factory method para criar instâncias dos modelos de dados
        
        Retorna tupla com:
            demanda_atual: Objeto DemandaAtual (demanda instantânea)
            demanda_acumulada: Objeto DemandaAcumulada (demanda cumulativa)
            capacidade_operacional: Objeto CapacidadeOperacional (capacidade produtiva)
        """
        # demanda_atual = DemandaAtual()
        demanda_acumulada = DemandaAcumulada()
        capacidade_operacional = CapacidadeOperacional()
        
        # return demanda_atual, demanda_acumulada, capacidade_operacional
        return demanda_acumulada, capacidade_operacional
        
    def calcular_acumulo_backlog(self, derivacao, capacidade, hora_inicio, hora_fim):
        acumulo = []
        total = 0

        for i, (d, c) in enumerate(zip(derivacao, capacidade)):
            if hora_inicio <= i <= hora_fim:
                total = d + total - c
                if total < 0:
                    total = 0
                acumulo.append(total)
            else:
                total = 0  # reset fora do horário
                acumulo.append(0)
        return acumulo