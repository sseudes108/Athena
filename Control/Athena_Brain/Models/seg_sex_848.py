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

def resolver_alocacao(MAX_ANALISTAS, streamlit):
    model = cp_model.CpModel()
    
    inicio_op = int(streamlit.inicio_op.split(':')[0])
    fim_op = int(streamlit.fim_op.split(':')[0]) + 1
      
    HORAS = list(range(inicio_op, fim_op))
    DEMANDA = streamlit.df_original['quantidade'].tolist()[inicio_op:fim_op]
    TMA_EM_SEGUNDOS = streamlit.tma
    PROPOSTAS_POR_HORA = int(3600 / TMA_EM_SEGUNDOS)
    HORAS_TRABALHADAS = 9
    HORAS_ALMOCO = [12, 13, 14]

    x = {}
    almoco = {}

    for a in range(MAX_ANALISTAS):
        for h in HORAS:
            x[a, h] = model.NewBoolVar(f"x_{a}_{h}")
        for h in HORAS_ALMOCO:
            almoco[a, h] = model.NewBoolVar(f"almoco_{a}_{h}")

    for a in range(MAX_ANALISTAS):
        model.Add(sum(x[a, h] for h in HORAS) == HORAS_TRABALHADAS)
        model.Add(sum(almoco[a, h] for h in HORAS_ALMOCO) == 1)
        for h in HORAS_ALMOCO:
            model.Add(x[a, h] == 0).OnlyEnforceIf(almoco[a, h])

    for i, h in enumerate(HORAS):
        model.Add(sum(x[a, h] for a in range(MAX_ANALISTAS)) * PROPOSTAS_POR_HORA >= DEMANDA[i])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0  # mais leve para cada rodada
    status = solver.Solve(model)

    solucao = []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for a in range(MAX_ANALISTAS):
            horas = [h for h in HORAS if solver.Value(x[a, h])]
            if horas:
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