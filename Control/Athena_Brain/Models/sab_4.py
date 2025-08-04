import math
from ortools.sat.python import cp_model
from Model.analista import Analista
import Control.manager_data as Data_Man

def encontrar_min_analistas(streamlit):
    min_analistas = 1  # Mínimo de 1 analista
    max_analistas = 100  # Máximo de 100 analistas
    melhor_solucao = None

    while min_analistas <= max_analistas:
        mid = (min_analistas + max_analistas) // 2
        print(f"Tentando com {mid} analistas...")
        status, solucao = resolver_alocacao(mid, streamlit)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            melhor_solucao = solucao
            max_analistas = mid - 1  # Tenta reduzir o número de analistas
        else:
            min_analistas = mid + 1  # Precisa de mais analistas

    return melhor_solucao

def resolver_alocacao(MAX_ANALISTAS, streamlit):
    model = cp_model.CpModel()
    
    # Horário de operação: 07:00 às 22:00
    inicio_op = int(streamlit.inicio_op.split(':')[0])
    fim_op = int(streamlit.fim_op.split(':')[0]) + 1
    HORAS = list(range(inicio_op, fim_op))
    DEMANDA = streamlit.df_original['quantidade'].tolist()[inicio_op : fim_op]
    TMA_EM_SEGUNDOS = streamlit.tma
    PROPOSTAS_POR_HORA = int(3600 / TMA_EM_SEGUNDOS)

    # Definição dos turnos possíveis de 4 horas
    TURNOS = [
        {'entrada': 7, 'saida': 11},  # 07:00 - 11:00
        {'entrada': 8, 'saida': 12},  # 08:00 - 12:00
        {'entrada': 9, 'saida': 13},  # 09:00 - 13:00
        {'entrada': 10, 'saida': 14}, # 10:00 - 14:00
        {'entrada': 11, 'saida': 15}, # 11:00 - 15:00
        {'entrada': 12, 'saida': 16}, # 12:00 - 16:00
        {'entrada': 13, 'saida': 17}, # 13:00 - 17:00
        {'entrada': 14, 'saida': 18}, # 14:00 - 18:00
        {'entrada': 15, 'saida': 19}, # 15:00 - 19:00
        {'entrada': 16, 'saida': 20}, # 16:00 - 20:00
        {'entrada': 17, 'saida': 21}, # 17:00 - 21:00
        {'entrada': 18, 'saida': 22}, # 18:00 - 22:00
        
        {'entrada': 7, 'saida': 9},  # 07:00 - 11:00
        {'entrada': 8, 'saida': 10},  # 08:00 - 12:00
        {'entrada': 9, 'saida': 11},  # 09:00 - 13:00
        {'entrada': 10, 'saida': 12}, # 10:00 - 14:00
    ]

    # Variáveis de decisão
    x = {}          # Indica se o analista 'a' trabalha na hora 'h'
    turno_analista = {}  # Indica qual turno o analista 'a' segue

    # Definir variáveis
    for a in range(MAX_ANALISTAS):
        # Cada analista está em exatamente um turno
        for t in range(len(TURNOS)):
            turno_analista[a, t] = model.NewBoolVar(f"turno_{a}_{t}")
        model.Add(sum(turno_analista[a, t] for t in range(len(TURNOS))) == 1)

        # Variáveis de trabalho por hora
        for h in HORAS:
            x[a, h] = model.NewBoolVar(f"x_{a}_{h}")

    # Adicionar constraints para trabalho
    for a in range(MAX_ANALISTAS):
        for t in range(len(TURNOS)):
            # Definir horas de trabalho para o turno t
            horas_trabalho = [h for h in HORAS if TURNOS[t]['entrada'] <= h < TURNOS[t]['saida']]
            
            # Para h em horas_trabalho: x[a, h] == 1
            for h in horas_trabalho:
                model.Add(x[a, h] == 1).OnlyEnforceIf(turno_analista[a, t])
            
            # Para h não em horas_trabalho: x[a, h] == 0
            for h in HORAS:
                if h not in horas_trabalho:
                    model.Add(x[a, h] == 0).OnlyEnforceIf(turno_analista[a, t])

    # Restrição de demanda por hora
    for i, h in enumerate(HORAS):
        if h == 7:
            required_demand = int(math.ceil(0.5 * DEMANDA[i]))  # Apenas metade pois é o acumulo noturno
            model.Add(sum(x[a, h] for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA >= required_demand)
        elif h == 9:
            required_demand = int(math.ceil(0.8 * DEMANDA[i]))  # Apenas metade pois é o acumulo noturno
            model.Add(sum(x[a, h] for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA >= required_demand)
        else:
            required_demand = int(math.ceil(1.1 * DEMANDA[i]))  # 30% de extra
            model.Add(sum(x[a, h] for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA >= required_demand)

    # Garantir acumulação zero às 10:00 e 22:00
    demanda_acumulada_10 = sum(DEMANDA[:HORAS.index(10)])
    capacidade_acumulada_10 = sum(sum(x[a, h] for h in HORAS[:HORAS.index(10)]) 
                                 for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA
    model.Add(capacidade_acumulada_10 >= demanda_acumulada_10)

    demanda_acumulada_22 = sum(DEMANDA)
    capacidade_acumulada_22 = sum(sum(x[a, h] for h in HORAS) 
                                 for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA
    model.Add(capacidade_acumulada_22 >= demanda_acumulada_22)

    # Resolver o modelo
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    solucao = []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for a in range(MAX_ANALISTAS):
            for t in range(len(TURNOS)):
                if solver.Value(turno_analista[a, t]):
                    horas = [h for h in HORAS if solver.Value(x[a, h])]
                    solucao.append((a, TURNOS[t], horas))
    return status, solucao

def athena(streamlit, calculadora):
    analistas = []
    capacidade_producao = [0] * len(streamlit.dataframe_sla['horario'].tolist())
    print(f"seg_sex_722.py Dem Ini - {sum(streamlit.demanda_inicial)}")
    
    solucao = encontrar_min_analistas(streamlit)
    
    # Inicializa a capacidade operacional no streamlit
    streamlit.capacidade_operacional.set_capacidade_operacao(capacidade_producao)
    
    for a, turno, horas in solucao:
        entrada = f"{turno['entrada']:02d}:00"
        saida = f"{turno['saida']:02d}:00"
        novo_analista = Analista(streamlit.tma, entrada, "00:00", saida)  # Sem almoço
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
    
    print(f"seg_sex_722.py Cap Ope - {sum(streamlit.capacidade_operacional.get_capacidade_operacao())}")
    return analistas