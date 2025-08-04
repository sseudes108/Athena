# Importação de modelos necessários
from Model.analista import Analista  # Classe que representa um analista
# from Model.demanda import DemandaAtual, DemandaAcumulada, CapacidadeOperacional  # Modelos de dados
import Control.manager_data as Data_Man
from Control.Athena_Brain.Models import seg_sex_722, seg_sex_848, sab_4
import Control.Athena_Brain.athena_lib as Brain
    
def calcular_capacity(streamlit, calculadora):
    """
    Função principal para cálculo de capacidade
    
    Parâmetros:
        tma: Tempo Médio de Atendimento (segundos)
        demanda_atual: Objeto DemandaAtual
        demanda_acumulada: Objeto DemandaAcumulada
        capacidade_operacional: Objeto CapacidadeOperacional
    
    Retorna:
        Lista de objetos Analista calculados
    """    
    # Chama o modelo de cálculo principal
    # response = modelo_01(streamlit, calculadora)
    # response = modelo_seg_sex_848(streamlit, calculadora)
    # response = modelo_seg_sex_722(streamlit, calculadora)
    response = modelo_sab_4(streamlit, calculadora)
        
    return response

def modelo_01(streamlit, calculadora):
    """
    Modelo de cálculo de capacidade baseado em picos de demanda
    
    Lógica principal:
        1. Adiciona analistas no turno da manhã até atender o pico matutino
        2. Adiciona analistas no turno da tarde/noite até atender o pico noturno
        3. Atualiza dados finais de capacidade e demanda
    
    Parâmetros:
        tma: Tempo Médio de Atendimento (segundos)
        demanda_atual: Objeto com demanda por hora
        demanda_acumulada: Objeto com demanda acumulada
        capacidade_operacional: Objeto para armazenar capacidade total
    
    Retorna:
        Lista de analistas alocados
    """
    
    PICO_MANHA = Data_Man.encontrar_indice_por_horario(streamlit.dataframe_sla, "10:00")  # Horário de pico matinal (10:00)
    PICO_NOITE = Data_Man.encontrar_indice_por_horario(streamlit.dataframe_sla, "21:00")  # Horário de pico noturno (21:00)
    
    analistas = []  # Lista para armazenar analistas alocados
    capacidade_producao  = streamlit.capacidade_operacional.get_capacidade_operacao()
    
    while streamlit.demanda_acumulada.get_demanda()[PICO_MANHA] > 0:
        novo_analista = Analista(streamlit.tma, "07:00", "12:00", "15:20")
        Brain.add_analista(streamlit, calculadora, analistas, capacidade_producao, novo_analista)
        
    while streamlit.demanda_acumulada.get_demanda()[PICO_NOITE] > 0:
        novo_analista = Analista(streamlit.tma, "13:40", "17:30", "22:00")
        Brain.add_analista(streamlit, calculadora, analistas, capacidade_producao, novo_analista)

    return analistas 

def modelo_seg_sex_848(streamlit, calculadora):    
    return seg_sex_848.athena(streamlit, calculadora)

def modelo_seg_sex_722(streamlit, calculadora):
    return seg_sex_722.athena(streamlit, calculadora)

def modelo_sab_4(streamlit, calculadora):
    return sab_4.athena(streamlit, calculadora)