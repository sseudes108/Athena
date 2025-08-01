# Módulo de orquestração de cálculos de capacidade
import streamlit as st
from itertools import accumulate  # Para cálculo cumulativo

import Control.athena as Athena  # Algoritmo principal de cálculo
from Model.analista import Analista
from Model.demanda import DemandaAtual, DemandaAcumulada, CapacidadeOperacional  # Modelos de dados

class Calculadora():   
    def athena(self, tma, demanda_atual, demanda_acumulada, capacidade_operacional):
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
        return Athena.calcular_capacity(tma, demanda_atual, demanda_acumulada, capacidade_operacional)

    def create_instancias(self):
        """
        Factory method para criar instâncias dos modelos de dados
        
        Retorna tupla com:
            demanda_atual: Objeto DemandaAtual (demanda instantânea)
            demanda_acumulada: Objeto DemandaAcumulada (demanda cumulativa)
            capacidade_operacional: Objeto CapacidadeOperacional (capacidade produtiva)
        """
        demanda_atual = DemandaAtual()
        demanda_acumulada = DemandaAcumulada()
        capacidade_operacional = CapacidadeOperacional()
        
        return demanda_atual, demanda_acumulada, capacidade_operacional
    
    def calcular_acumulo(self, derivacao):
        """
        Calcula demanda acumulada a partir de valores instantâneos
        
        Parâmetros:
            derivacao: Lista de valores de demanda por período
            
        Retorna:
            Lista cumulativa usando função accumulate do itertools
            Ex: [1, 2, 3] → [1, 3, 6]
        """
        acumulo = list(accumulate(derivacao))
        return acumulo
    
    @staticmethod
    def add_analista(entrada, almoco, saida):
        novo_analista = Analista(st.session_state.tma, entrada, almoco, saida)
        st.session_state.analistas_lista.append(novo_analista)
        
        capacidade_atual = st.session_state.capacidade_operacional.get_capacidade_producao()
        capacidade_atualizada = [a + b for a, b in zip(capacidade_atual, novo_analista.get_capacidade_producao())]
        
        st.session_state.capacidade_operacional.set_capacidade_producao(capacidade_atualizada)
    
    @staticmethod
    def rem_analista(entrada, almoco, saida):
        analista = Analista(st.session_state.tma, entrada, almoco, saida)
        for i in range(len(st.session_state.analistas_lista)):
            
            if st.session_state.analistas_lista[i].get_horarios()[0] == entrada:
                if st.session_state.analistas_lista[i].get_horarios()[1] == almoco:
                    if st.session_state.analistas_lista[i].get_horarios()[2] == saida:
                        st.session_state.novo_analista.remove(st.session_state.analistas_lista[i])
                        break
        
        capacidade_atual = st.session_state.capacidade_operacional.get_capacidade_producao()
        capacidade_atualizada = [a - b for a, b in zip(capacidade_atual, analista.get_capacidade_producao())]
        
        st.session_state.capacidade_operacional.set_capacidade_producao(capacidade_atualizada)