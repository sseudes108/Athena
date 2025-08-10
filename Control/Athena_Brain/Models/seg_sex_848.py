import math
from ortools.sat.python import cp_model
from Model.analista import Analista
import Control.manager_data as Data_Man

def encontrar_min_analistas(streamlit):
    min_analistas = 1
    max_analistas = 100
    melhor_solucao = None

    while min_analistas <= max_analistas:
        mid = (min_analistas + max_analistas) // 2
        print(f"Tentando com {mid} analistas...")
        status, solucao = resolver_alocacao(mid, streamlit)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            melhor_solucao = solucao
            max_analistas = mid - 1  # tenta reduzir ainda mais
        else:
            min_analistas = mid + 1  # precisa de mais analistas

    return melhor_solucao

# def resolver_alocacao(MAX_ANALISTAS, streamlit):
#     model = cp_model.CpModel()
    
#     inicio_op = int(streamlit.inicio_op.split(':')[0])
#     fim_op = int(streamlit.fim_op.split(':')[0]) + 1
      
#     HORAS = list(range(inicio_op, fim_op))
#     DEMANDA = [int(math.ceil(d)) for d in streamlit.df_original['quantidade'].tolist()[inicio_op:fim_op]]
#     TMA_EM_SEGUNDOS = streamlit.tma
#     PROPOSTAS_POR_HORA = int(3600 / TMA_EM_SEGUNDOS)
#     HORAS_TRABALHADAS = 9
#     HORAS_ALMOCO = [12, 13, 14]

#     # Variáveis de decisão
#     x = {}          # Indica se o analista 'a' trabalha na hora 'h'
#     almoco = {}     # Indica o horário de almoço do analista 'a'
#     ativo = {}      # Indica se o analista 'a' está sendo utilizado

#     # 1. Criar variáveis para controle de analistas ativos
#     for a in range(MAX_ANALISTAS):
#         ativo[a] = model.NewBoolVar(f"ativo_{a}")
        
#         for h in HORAS:
#             x[a, h] = model.NewBoolVar(f"x_{a}_{h}")
            
#         for h in HORAS_ALMOCO:
#             almoco[a, h] = model.NewBoolVar(f"almoco_{a}_{h}")

#     # 2. Restrições por analista (só aplicáveis se o analista estiver ativo)
#     for a in range(MAX_ANALISTAS):
#         # Se inativo, não trabalha em nenhuma hora
#         for h in HORAS:
#             model.Add(x[a, h] == 0).OnlyEnforceIf(ativo[a].Not())
        
#         # Se ativo, deve cumprir jornada completa
#         model.Add(sum(x[a, h] for h in HORAS) == HORAS_TRABALHADAS).OnlyEnforceIf(ativo[a])
        
#         # Se ativo, deve ter exatamente 1 horário de almoço
#         model.Add(sum(almoco[a, h] for h in HORAS_ALMOCO) == 1).OnlyEnforceIf(ativo[a])
        
#         # Durante o almoço, não trabalha
#         for h in HORAS_ALMOCO:
#             model.Add(x[a, h] == 0).OnlyEnforceIf(almoco[a, h])

#     # 3. Modelagem do backlog
#     backlog = [0]  # Backlog inicial = 0
#     for i, h in enumerate(HORAS):
#         capacidade_h = model.NewIntVar(0, MAX_ANALISTAS * PROPOSTAS_POR_HORA, f'capacidade_{h}')
#         model.Add(capacidade_h == sum(x[a, h] for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA)
        
#         demanda_acumulada = model.NewIntVar(0, 1000000, f'demanda_acumulada_{h}')
#         model.Add(demanda_acumulada == backlog[i] + DEMANDA[i])
        
#         backlog_next = model.NewIntVar(0, 1000000, f'backlog_next_{h}')
#         model.Add(backlog_next >= demanda_acumulada - capacidade_h)
#         model.Add(backlog_next >= 0)
#         backlog.append(backlog_next)
    
#     model.Add(backlog[-1] == 0)  # Backlog final zero

#     # 4. Objetivo: Minimizar o número total de analistas ativos
#     total_analistas = model.NewIntVar(0, MAX_ANALISTAS, 'total_analistas')
#     model.Add(total_analistas == sum(ativo[a] for a in range(MAX_ANALISTAS)))
#     model.Minimize(total_analistas)

#     # 5. Estratégias para acelerar a resolução
#     solver = cp_model.CpSolver()
#     solver.parameters.max_time_in_seconds = 120.0
#     solver.parameters.num_search_workers = 8  # Usar paralelismo
#     status = solver.Solve(model)

#     # Recuperar solução
#     solucao = []
#     if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
#         for a in range(MAX_ANALISTAS):
#             if solver.Value(ativo[a]):
#                 horas = [h for h in HORAS if solver.Value(x[a, h])]
#                 almoco_h = next((h for h in HORAS_ALMOCO if solver.Value(almoco[a, h])), None)
#                 solucao.append((a, horas, almoco_h))
#     return status, solucao

def resolver_alocacao(MAX_ANALISTAS, streamlit):
    model = cp_model.CpModel()
    
    inicio_op = int(streamlit.inicio_op.split(':')[0])
    fim_op = int(streamlit.fim_op.split(':')[0]) + 1
      
    HORAS = list(range(inicio_op, fim_op))
    DEMANDA = [int(math.ceil(d)) for d in streamlit.df_original['quantidade'].tolist()[inicio_op:fim_op]]
    TMA_EM_SEGUNDOS = streamlit.tma
    
    # Fator de escala para lidar com capacidades fracionárias
    FATOR_ESCALA = 1000
    HORAS_TRABALHADAS = 9
    HORAS_ALMOCO = [12, 13, 14]

    # Calcular capacidade por analista com precisão
    if TMA_EM_SEGUNDOS > 0:
        capacidade_por_analista = (3600 / TMA_EM_SEGUNDOS) * FATOR_ESCALA
    else:
        capacidade_por_analista = 0

    # Variáveis de decisão
    x = {}          # Indica se o analista 'a' trabalha na hora 'h'
    almoco = {}     # Indica o horário de almoço do analista 'a'
    ativo = {}      # Indica se o analista 'a' está sendo utilizado

    # 1. Criar variáveis para controle de analistas ativos
    for a in range(MAX_ANALISTAS):
        ativo[a] = model.NewBoolVar(f"ativo_{a}")
        
        for h in HORAS:
            x[a, h] = model.NewBoolVar(f"x_{a}_{h}")
            
        for h in HORAS_ALMOCO:
            almoco[a, h] = model.NewBoolVar(f"almoco_{a}_{h}")

    # 2. Restrições por analista
    for a in range(MAX_ANALISTAS):
        # Se inativo, não trabalha em nenhuma hora
        for h in HORAS:
            model.Add(x[a, h] == 0).OnlyEnforceIf(ativo[a].Not())
        
        # Se ativo, deve cumprir jornada completa
        model.Add(sum(x[a, h] for h in HORAS) == HORAS_TRABALHADAS).OnlyEnforceIf(ativo[a])
        
        # Se ativo, deve ter exatamente 1 horário de almoço
        model.Add(sum(almoco[a, h] for h in HORAS_ALMOCO) == 1).OnlyEnforceIf(ativo[a])
        
        # Durante o almoço, não trabalha
        for h in HORAS_ALMOCO:
            model.Add(x[a, h] == 0).OnlyEnforceIf(almoco[a, h])

    # 3. Modelagem do backlog com tratamento preciso para capacidade fracionária
    backlog = [0]  # Backlog inicial = 0
    
    # Escalar demanda e capacidade
    demanda_escalada = [d * FATOR_ESCALA for d in DEMANDA]
    
    for i, h in enumerate(HORAS):
        # Calcular capacidade total na hora h (em unidades escaladas)
        capacidade_total = model.NewIntVar(0, MAX_ANALISTAS * int(capacidade_por_analista) * 2, f'capacidade_{h}')
        
        # Soma do número de analistas trabalhando na hora h
        num_analistas = model.NewIntVar(0, MAX_ANALISTAS, f'num_analistas_{h}')
        model.Add(num_analistas == sum(x[a, h] for a in range(MAX_ANALISTAS)))
        
        # Capacidade = num_analistas * capacidade_por_analista
        capacidade_calc = model.NewIntVar(0, MAX_ANALISTAS * int(capacidade_por_analista) * 2, f'capacidade_calc_{h}')
        model.AddMultiplicationEquality(capacidade_calc, [num_analistas, int(capacidade_por_analista)])
        
        # Ajustar para escala
        model.Add(capacidade_total == capacidade_calc)
        
        demanda_acumulada = model.NewIntVar(0, 100000000, f'demanda_acumulada_{h}')
        model.Add(demanda_acumulada == backlog[i] + demanda_escalada[i])
        
        backlog_next = model.NewIntVar(0, 100000000, f'backlog_next_{h}')
        model.Add(backlog_next >= demanda_acumulada - capacidade_total)
        model.Add(backlog_next >= 0)
        backlog.append(backlog_next)
    
    model.Add(backlog[-1] == 0)  # Backlog final zero

    # 4. Objetivo: Minimizar o número total de analistas ativos
    total_analistas = model.NewIntVar(0, MAX_ANALISTAS, 'total_analistas')
    model.Add(total_analistas == sum(ativo[a] for a in range(MAX_ANALISTAS)))
    model.Minimize(total_analistas)

    # 5. Estratégias para resolver problemas difíceis
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 8
    
    # Para problemas complexos com TMA grande
    if TMA_EM_SEGUNDOS > 3600:
        solver.parameters.linearization_level = 0
        solver.parameters.cp_model_presolve = False

    status = solver.Solve(model)

    # Recuperar solução
    solucao = []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for a in range(MAX_ANALISTAS):
            if solver.Value(ativo[a]):
                horas = [h for h in HORAS if solver.Value(x[a, h])]
                almoco_h = next((h for h in HORAS_ALMOCO if solver.Value(almoco[a, h])), None)
                solucao.append((a, horas, almoco_h))
    return status, solucao
    
def athena(streamlit, calculadora):
    analistas = []
    capacidade_producao = [0] * len(streamlit.dataframe_sla['horario'].tolist())
    print(f"seg_sex_848.py Dem Ini - {sum(streamlit.demanda_inicial)}")
    
    solucao = encontrar_min_analistas(streamlit)
    
    entrada = "08:00"
    saida = "17:48"
    
    # Inicializa a capacidade operacional no streamlit
    streamlit.capacidade_operacional.set_capacidade_operacao(capacidade_producao)
    
    for _, _, almoco_h in solucao:
        almoco = f"{almoco_h}:00"
        novo_analista = Analista(streamlit.tma, entrada, almoco, saida)
        analistas.append(novo_analista)
        
        # Obtém a capacidade atual de streamlit
        capacidade_atual = streamlit.capacidade_operacional.get_capacidade_operacao()
        
        # Calcula a nova capacidade
        capacidade_nova = [a + b for a, b in zip(capacidade_atual, novo_analista.get_capacidade_operacao())]
        
        # Atualiza o objeto streamlit
        streamlit.capacidade_operacional.set_capacidade_operacao(capacidade_nova)
        
        acumulo_atualizado = calculadora.calcular_acumulo_backlog(
                streamlit.demanda_inicial, 
                capacidade_nova,
                Data_Man.encontrar_proximo_indice(streamlit.dataframe_sla, streamlit.inicio_op),
                Data_Man.encontrar_proximo_indice(streamlit.dataframe_sla, streamlit.fim_op)
            )
        streamlit.demanda_acumulada.set_demanda(acumulo_atualizado)
    
    print(f"seg_sex_848.py Cap Ope - {sum(streamlit.capacidade_operacional.get_capacidade_operacao())}")
    return analistas