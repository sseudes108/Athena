import math
from ortools.sat.python import cp_model
from Model.analista import Analista
import Control.manager_data as Data_Man

def encontrar_min_analistas(streamlit):
    min_analistas = 1  # Mínimo de 10 analistas conforme requisito
    max_analistas = 100  # Máximo de 100 analistas conforme requisito
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
    DEMANDA = [int(math.ceil(d)) for d in streamlit.df_original['quantidade'].tolist()[inicio_op : fim_op]]
    TMA_EM_SEGUNDOS = streamlit.tma
    PROPOSTAS_POR_HORA = int(3600 / TMA_EM_SEGUNDOS)

    # Definição dos turnos possíveis (apenas turnos de 7h20 + 1h de almoço)
    TURNOS = [
        {'entrada': 7, 'saida': 15.334},   # 07:00 - 15:20
        {'entrada': 8, 'saida': 16.334},   # 08:00 - 16:20
        {'entrada': 9, 'saida': 17.334},   # 09:00 - 17:20
        {'entrada': 10, 'saida': 18.334},  # 10:00 - 18:20
        {'entrada': 11, 'saida': 19.334},  # 11:00 - 19:20
        {'entrada': 12, 'saida': 20.334},  # 12:00 - 20:20
        {'entrada': 13, 'saida': 21.334},  # 13:00 - 21:20
        {'entrada': 13.667, 'saida': 22},  # 13:40 - 22:00
    ]
    
    # Variáveis de decisão
    x = {}          # Indica se o analista 'a' trabalha na hora 'h'
    almoco = {}     # Indica o horário de almoço do analista 'a'
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

        # Variáveis de almoço para todas as horas
        for h in HORAS:
            almoco[a, h] = model.NewBoolVar(f"almoco_{a}_{h}")

    # Adicionar constraints para almoço e trabalho
    for a in range(MAX_ANALISTAS):
        for t in range(len(TURNOS)):
            entrada = TURNOS[t]['entrada']
            saida = TURNOS[t]['saida']
            almoco_possiveis_t = [h for h in HORAS if h >= entrada + 4 and h + 1 <= saida - 2]
            model.Add(sum(almoco[a, h] for h in almoco_possiveis_t) == 1).OnlyEnforceIf(turno_analista[a, t])
            for h in HORAS:
                if h not in almoco_possiveis_t:
                    model.Add(almoco[a, h] == 0).OnlyEnforceIf(turno_analista[a, t])
            
            horas_trabalho = [h for h in HORAS if entrada <= h < saida]
            if saida % 1 != 0:
                horas_trabalho = horas_trabalho[:-1]
            
            for h in horas_trabalho:
                model.Add(x[a, h] == 1).OnlyEnforceIf([turno_analista[a, t], almoco[a, h].Not()])
                model.Add(x[a, h] == 0).OnlyEnforceIf([turno_analista[a, t], almoco[a, h]])
            
            for h in HORAS:
                if h not in horas_trabalho:
                    model.Add(x[a, h] == 0).OnlyEnforceIf(turno_analista[a, t])

    # Definir capacidade por hora
    capacity = []
    for i, h in enumerate(HORAS):
        c = model.NewIntVar(0, MAX_ANALISTAS * PROPOSTAS_POR_HORA, f"capacity_{h}")
        model.Add(c == sum(x[a, h] for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA)
        capacity.append(c)

    # Definir backlog e effective demand
    backlog = [0]  # backlog inicial = 0
    for i, h in enumerate(HORAS):
        effective = model.NewIntVar(0, 100000, f"effective_{h}")
        model.Add(effective == backlog[-1] + DEMANDA[i])

        b = model.NewIntVar(0, 100000, f"backlog_{h}")
        model.Add(b >= effective - capacity[i])
        model.Add(b >= 0)
        backlog.append(b)

        # Multiplicador baseado no horário
        multiplier = 0.1

        k = int(multiplier * 10)
        mult_var = model.NewIntVar(0, 1000000, f"mult_{h}")
        model.AddMultiplicationEquality(mult_var, [effective, model.NewConstant(k)])

        add_var = model.NewIntVar(0, 1000000, f"add_{h}")
        model.Add(add_var == mult_var + 9)

        req_var = model.NewIntVar(0, 100000, f"req_{h}")
        model.AddDivisionEquality(req_var, add_var, 10)

        model.Add(capacity[i] >= req_var)

    # Constraint específica para capacidade de 7+8+9 >= demanda de 7 * 1.15
    required_capacity = int(math.ceil(DEMANDA[0] * 1.15))
    model.Add(sum(capacity[0:3]) >= required_capacity)

    # Garantir acumulação zero às 22:00
    model.Add(backlog[-1] == 0)  # Após hora 21:00

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
                    almoco_h = next((h for h in HORAS if solver.Value(almoco[a, h])), None)
                    solucao.append((a, TURNOS[t], horas, almoco_h))
    return status, solucao

def athena(streamlit, calculadora):
    analistas = []
    capacidade_producao = [0] * len(streamlit.dataframe_sla['horario'].tolist())
    print(f"seg_sex_722.py Dem Ini - {sum(streamlit.demanda_inicial)}")
    
    solucao = encontrar_min_analistas(streamlit)
    
    # Inicializa a capacidade operacional no streamlit
    streamlit.capacidade_operacional.set_capacidade_operacao(capacidade_producao)
    
    for a, turno, horas, almoco_h in solucao:
        entrada_hora = int(turno['entrada'])
        entrada_minutos = int((turno['entrada'] % 1) * 60)
        entrada = f"{entrada_hora:02d}:{entrada_minutos:02d}"
        saida = (f"{int(turno['saida']):02d}:{int((turno['saida'] % 1) * 60):02d}" 
                if turno['saida'] % 1 != 0 else f"{int(turno['saida']):02d}:00")
        almoco = f"{almoco_h}:00"  # Sempre usa o horário de almoço calculado
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
    
    print(f"seg_sex_722.py Cap Ope - {sum(streamlit.capacidade_operacional.get_capacidade_operacao())}")
    return analistas