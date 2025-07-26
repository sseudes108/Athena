from Model.analista import Analista
from Model.demanda import DemandaAtual, DemandaAcumulada, CapacidadeOperacional


def calcular_capacity(tma, demanda_atual, demanda_acumulada, capacidade_operacional):
    print("Calculando Capacity")
    
    response = modelo_01(
        tma,
        demanda_atual, 
        demanda_acumulada, 
        capacidade_operacional
    )
    
    return response

def modelo_01(tma, demanda_atual:DemandaAtual, demanda_acumulada:DemandaAcumulada, capacidade_operacional:CapacidadeOperacional):
    PICO_MANHA = 10
    PICO_NOITE = 21
    analistas = []
 
    while demanda_acumulada.get_demanda()[PICO_MANHA] > 0:
        novo_analista = Analista(tma, "07:00", "12:00", "15:20")
        analistas.append(novo_analista)
        
        demanda_atualizada = [a - b for a, b in zip(demanda_atual.get_demanda(), novo_analista.get_capacidade_producao())]
        
        demanda_atual.set_demanda(demanda_atualizada)
        demanda_acumulada.recalcular_acumulo(demanda_atualizada)
        
    while demanda_acumulada.get_demanda()[PICO_NOITE] > 0:
        novo_analista = Analista(tma, "13:40", "17:25", "22:00")
        analistas.append(novo_analista)
        
        demanda_atualizada = [a - b for a, b in zip(demanda_atual.get_demanda(), novo_analista.get_capacidade_producao())]
        
        demanda_atual.set_demanda(demanda_atualizada)
        demanda_acumulada.recalcular_acumulo(demanda_atualizada)
                
    capacidade_producao_atualizada = [0] * 24
    for analista in analistas:
        capacidade = analista.get_capacidade_producao()
        capacidade_producao_atualizada = [a + b for a, b in zip(capacidade_producao_atualizada, capacidade)]
    
    acumulo_final_sem_negativos = [max(0, v) for v in demanda_atual.get_demanda()]
    demanda_acumulada.set_demanda(acumulo_final_sem_negativos)
    capacidade_operacional.set_capacidade_producao(capacidade_producao_atualizada)
       
    return analistas

def main():
    pass

if __name__ == '__main__':
    main()