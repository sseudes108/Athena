# Módulo de orquestração de cálculos de capacidade

import Control.athena as Athena  # Algoritmo principal de cálculo

import Control.manager_data as Data_Man

from Model.analista import Analista
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
    
    def add_analista(self, entrada, almoco, saida):
        analistas = self.streamlit.session_state.analistas_lista
        novo_analista = Analista(self.streamlit.session_state.tma, entrada, almoco, saida)
        analistas.append(novo_analista)
        
        # Obtém a capacidade atual de streamlit
        capacidade_atual = self.streamlit.session_state.capacidade_operacional.get_capacidade_operacao()
        
        # Calcula a nova capacidade
        capacidade_nova = [a + b for a, b in zip(capacidade_atual, novo_analista.get_capacidade_operacao())]
        
        # Atualiza o objeto streamlit
        self.streamlit.session_state.capacidade_operacional.set_capacidade_operacao(capacidade_nova)
        
        acumulo_atualizado = self.calcular_acumulo_backlog(
                self.streamlit.session_state.demanda_inicial, 
                capacidade_nova,
                Data_Man.encontrar_proximo_indice(self.streamlit.session_state.dataframe_sla, self.streamlit.session_state.inicio_op),
                Data_Man.encontrar_proximo_indice(self.streamlit.session_state.dataframe_sla, self.streamlit.session_state.fim_op)
            )
        self.streamlit.session_state.demanda_acumulada.set_demanda(acumulo_atualizado)
        
        self.streamlit.analistas_lista = analistas
        self.streamlit.session_state.action_user = 'add'
    
    def rem_analista(self, entrada, almoco, saida):
        analistas = self.streamlit.session_state.analistas_lista
        
        # Encontrar e remover o primeiro analista com os horários correspondentes
        for i, analista in enumerate(analistas):
            if (Data_Man.datetime_to_str(analista.entrada) == entrada and 
                Data_Man.datetime_to_str(analista.almoco) == almoco and 
                Data_Man.datetime_to_str(analista.saida) == saida):
                
                # Guarda o analista antes de remover para usar na capacidade
                analista_removido = analistas.pop(i)
                break
        else:
            # Se nenhum analista foi encontrado, sair da função
            return

        # Atualiza a lista de analistas no session_state
        self.streamlit.session_state.analistas_lista = analistas
        
        # Obtém a capacidade atual
        capacidade_atual = self.streamlit.session_state.capacidade_operacional.get_capacidade_operacao()
        
        # Calcula a nova capacidade SUBTRAINDO a capacidade do analista removido
        capacidade_nova = [a - b for a, b in zip(capacidade_atual, analista_removido.get_capacidade_operacao())]
        
        # Atualiza o objeto streamlit
        self.streamlit.session_state.capacidade_operacional.set_capacidade_operacao(capacidade_nova)
        
        acumulo_atualizado = self.calcular_acumulo_backlog(
                self.streamlit.session_state.demanda_inicial, 
                capacidade_nova,
                Data_Man.encontrar_proximo_indice(self.streamlit.session_state.dataframe_sla, self.streamlit.session_state.inicio_op),
                Data_Man.encontrar_proximo_indice(self.streamlit.session_state.dataframe_sla, self.streamlit.session_state.fim_op)
            )
        self.streamlit.session_state.demanda_acumulada.set_demanda(acumulo_atualizado)
        
        self.streamlit.analistas_lista = analistas
        self.streamlit.session_state.action_user = 'rem'