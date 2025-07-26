# Importação de modelos necessários
from Model.analista import Analista  # Classe que representa um analista
from Model.demanda import DemandaAtual, DemandaAcumulada, CapacidadeOperacional  # Modelos de dados

def calcular_capacity(tma, demanda_atual, demanda_acumulada, capacidade_operacional):
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
    print("Calculando Capacity")  # Indicador de início do cálculo
    
    # Chama o modelo de cálculo principal
    response = modelo_01(
        tma,
        demanda_atual, 
        demanda_acumulada, 
        capacidade_operacional
    )
    
    return response

def modelo_01(tma, demanda_atual:DemandaAtual, demanda_acumulada:DemandaAcumulada, capacidade_operacional:CapacidadeOperacional):
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
    # Definição dos horários de pico (índices das horas)
    PICO_MANHA = 10  # Horário de pico matinal (10:00)
    PICO_NOITE = 21  # Horário de pico noturno (21:00)
    
    analistas = []  # Lista para armazenar analistas alocados

    # Fase 1: Atendimento ao pico da manhã
    while demanda_acumulada.get_demanda()[PICO_MANHA] > 0:
        # Cria novo analista com jornada fixa para turno da manhã
        novo_analista = Analista(tma, "07:00", "12:00", "15:20")
        analistas.append(novo_analista)
        
        # Atualiza demanda subtraindo a capacidade do novo analista
        demanda_atualizada = [a - b for a, b in zip(demanda_atual.get_demanda(), novo_analista.get_capacidade_producao())]
        
        # Atualiza objetos de demanda
        demanda_atual.set_demanda(demanda_atualizada)
        demanda_acumulada.recalcular_acumulo(demanda_atualizada)
        
    # Fase 2: Atendimento ao pico da noite
    while demanda_acumulada.get_demanda()[PICO_NOITE] > 0:
        # Cria novo analista com jornada fixa para turno da tarde/noite
        novo_analista = Analista(tma, "13:40", "17:25", "22:00")
        analistas.append(novo_analista)
        
        # Atualiza demanda subtraindo a capacidade do novo analista
        demanda_atualizada = [a - b for a, b in zip(demanda_atual.get_demanda(), novo_analista.get_capacidade_producao())]
        
        # Atualiza objetos de demanda
        demanda_atual.set_demanda(demanda_atualizada)
        demanda_acumulada.recalcular_acumulo(demanda_atualizada)
                
    # Cálculo da capacidade total de produção
    capacidade_producao_atualizada = [0] * 24  # Inicializa com zeros
    for analista in analistas:
        capacidade = analista.get_capacidade_producao()
        # Soma capacidade de todos os analistas
        capacidade_producao_atualizada = [a + b for a, b in zip(capacidade_producao_atualizada, capacidade)]
    
    # Garante que não há valores negativos no acumulo
    acumulo_final_sem_negativos = [max(0, v) for v in demanda_atual.get_demanda()]
    demanda_acumulada.set_demanda(acumulo_final_sem_negativos)
    
    # Atualiza objeto de capacidade operacional
    capacidade_operacional.set_capacidade_producao(capacidade_producao_atualizada)
       
    return analistas  # Retorna lista de analistas alocados



# from Model.analista import Analista
# from Model.demanda import DemandaAtual, DemandaAcumulada, CapacidadeOperacional


# def calcular_capacity(tma, demanda_atual, demanda_acumulada, capacidade_operacional):
#     print("Calculando Capacity")
    
#     response = modelo_01(
#         tma,
#         demanda_atual, 
#         demanda_acumulada, 
#         capacidade_operacional
#     )
    
#     return response

# def modelo_01(tma, demanda_atual:DemandaAtual, demanda_acumulada:DemandaAcumulada, capacidade_operacional:CapacidadeOperacional):
#     PICO_MANHA = 10
#     PICO_NOITE = 21
#     analistas = []
 
#     while demanda_acumulada.get_demanda()[PICO_MANHA] > 0:
#         novo_analista = Analista(tma, "07:00", "12:00", "15:20")
#         analistas.append(novo_analista)
        
#         demanda_atualizada = [a - b for a, b in zip(demanda_atual.get_demanda(), novo_analista.get_capacidade_producao())]
        
#         demanda_atual.set_demanda(demanda_atualizada)
#         demanda_acumulada.recalcular_acumulo(demanda_atualizada)
        
#     while demanda_acumulada.get_demanda()[PICO_NOITE] > 0:
#         novo_analista = Analista(tma, "13:40", "17:25", "22:00")
#         analistas.append(novo_analista)
        
#         demanda_atualizada = [a - b for a, b in zip(demanda_atual.get_demanda(), novo_analista.get_capacidade_producao())]
        
#         demanda_atual.set_demanda(demanda_atualizada)
#         demanda_acumulada.recalcular_acumulo(demanda_atualizada)
                
#     capacidade_producao_atualizada = [0] * 24
#     for analista in analistas:
#         capacidade = analista.get_capacidade_producao()
#         capacidade_producao_atualizada = [a + b for a, b in zip(capacidade_producao_atualizada, capacidade)]
    
#     acumulo_final_sem_negativos = [max(0, v) for v in demanda_atual.get_demanda()]
#     demanda_acumulada.set_demanda(acumulo_final_sem_negativos)
#     capacidade_operacional.set_capacidade_producao(capacidade_producao_atualizada)
       
#     return analistas

# def main():
#     pass

# if __name__ == '__main__':
#     main()