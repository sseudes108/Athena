from datetime import datetime, timedelta
import streamlit as st

# Importação de modelos necessários
from Model.analista import Analista  # Classe que representa um analista
from Model.demanda import DemandaAtual, DemandaAcumulada, CapacidadeOperacional  # Modelos de dados
import Control.manager_data as Data_Man

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
    # Chama o modelo de cálculo principal
    response = modelo_01(
        tma,
        demanda_atual, 
        demanda_acumulada, 
        capacidade_operacional
    )
    
    # response = modelo_otimizado(
    #     tma,
    #     demanda_atual, 
    #     demanda_acumulada, 
    #     capacidade_operacional
    # )
    
    return response

def modelo_otimizado(tma, demanda_atual, demanda_acumulada, capacidade_operacional):
    df_sla = st.session_state.dataframe_sla.reset_index(drop=True)
    sla_minutos = st.session_state.sla
    horarios_possiveis = df_sla["horario"].tolist()

    def str_to_time(hstr): return datetime.strptime(hstr, "%H:%M")

    hora_inicio = str_to_time(st.session_state.inicio_op)
    hora_fim = str_to_time(st.session_state.fim_op)

    analistas = []

    def encontrar_melhor_almoco(entrada, saida):
        almoco_duracao = timedelta(minutes=60)
        inicio_min = entrada + timedelta(hours=4)
        fim_max = saida - timedelta(hours=1.5)

        menor_demanda = float("inf")
        melhor_horario = None

        for i, h in enumerate(horarios_possiveis):
            h_dt = h
            fim_h = h_dt + almoco_duracao
            if h_dt >= inicio_min and fim_h <= fim_max:
                indices = [j for j, x in enumerate(horarios_possiveis) if h_dt <= x < fim_h]
                demanda_total = sum(demanda_atual.get_demanda()[j] for j in indices)
                if demanda_total < menor_demanda:
                    menor_demanda = demanda_total
                    melhor_horario = h_dt
        return melhor_horario

    def criar_e_aplicar_analista(entrada_str, duracao_horas, commit=True):
        entrada_dt = str_to_time(entrada_str)
        saida_dt = entrada_dt + timedelta(hours=duracao_horas)
        almoco_dt = encontrar_melhor_almoco(entrada_dt, saida_dt)
        if almoco_dt is None:
            return None

        analista = Analista(tma, entrada_dt.strftime("%H:%M"),
                            almoco_dt.strftime("%H:%M"),
                            saida_dt.strftime("%H:%M"))
        if commit:
            analistas.append(analista)
            nova_demanda = [a - b for a, b in zip(demanda_atual.get_demanda(), analista.get_capacidade_producao())]
            demanda_atual.set_demanda(nova_demanda)
            demanda_acumulada.recalcular_acumulo(nova_demanda)
        return analista

    horario_atual = hora_inicio
    entradas_validas = []
    while horario_atual + timedelta(hours=6) <= hora_fim:
        entradas_validas.append(horario_atual.strftime("%H:%M"))
        horario_atual += timedelta(minutes=sla_minutos)

    MAX_ANALISTAS = 300
    while max(demanda_acumulada.get_demanda()) > 0 and len(analistas) < MAX_ANALISTAS:
        melhor_entrada = None
        menor_residuo = float("inf")
        melhor_analista = None

        demanda_snapshot = demanda_atual.get_demanda()[:]
        acumulada_snapshot = demanda_acumulada.get_demanda()[:]

        for entrada in entradas_validas:
            analista_teste = criar_e_aplicar_analista(entrada, 8, commit=False)
            if not analista_teste:
                continue

            impacto = sum(max(0, v) for v in [
                a - b for a, b in zip(acumulada_snapshot, analista_teste.get_capacidade_producao())
            ])

            if impacto < menor_residuo:
                melhor_entrada = entrada
                menor_residuo = impacto
                melhor_analista = analista_teste

        if melhor_analista:
            analistas.append(melhor_analista)
            nova_demanda = [a - b for a, b in zip(demanda_atual.get_demanda(), melhor_analista.get_capacidade_producao())]
            demanda_atual.set_demanda(nova_demanda)
            demanda_acumulada.recalcular_acumulo(nova_demanda)
        else:
            break  # Nenhum candidato útil

    capacidade_producao_atualizada = [0] * len(demanda_atual.get_demanda())
    for analista in analistas:
        capacidade = analista.get_capacidade_producao()
        capacidade_producao_atualizada = [a + b for a, b in zip(capacidade_producao_atualizada, capacidade)]

    demanda_final = [max(0, v) for v in demanda_atual.get_demanda()]
    demanda_acumulada.set_demanda(demanda_final)
    capacidade_operacional.set_capacidade_producao(capacidade_producao_atualizada)

    return analistas

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
    
    PICO_MANHA = Data_Man.encontrar_indice_por_horario(st.session_state.dataframe_sla, "10:00")  # Horário de pico matinal (10:00)
    PICO_NOITE = Data_Man.encontrar_indice_por_horario(st.session_state.dataframe_sla, "21:00")  # Horário de pico noturno (21:00)
    
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
        novo_analista = Analista(tma, "13:40", "17:30", "22:00")
        analistas.append(novo_analista)
        
        # Atualiza demanda subtraindo a capacidade do novo analista
        demanda_atualizada = [a - b for a, b in zip(demanda_atual.get_demanda(), novo_analista.get_capacidade_producao())]
        
        # Atualiza objetos de demanda
        demanda_atual.set_demanda(demanda_atualizada)
        demanda_acumulada.recalcular_acumulo(demanda_atualizada)
                
    # Cálculo da capacidade total de produção
    capacidade_producao_atualizada = [0] * len(demanda_atualizada)  # Inicializa com zeros
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