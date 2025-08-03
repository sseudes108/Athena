import Control.manager_data as Data_Man

def add_analista(streamlit, calculadora, analistas, novo_analista):
    analistas.append(novo_analista)
    
    # Obtém a capacidade atual de streamlit
    capacidade_atual = streamlit.capacidade_operacional.get_capacidade_operacao()
    
    # Calcula a nova capacidade
    capacidade_nova = [a + b for a, b in zip(capacidade_atual, novo_analista.get_capacidade_operacao())]
    
    # Atualiza o objeto streamlit
    streamlit.capacidade_operacional.set_capacidade_operacao(capacidade_nova)
    
    acumulo_atualizado = calculadora.calcular_acumulop_backlog(
            streamlit.demanda_inicial, 
            capacidade_nova,
            Data_Man.encontrar_proximo_indice(streamlit.dataframe_sla, streamlit.inicio_op),
            Data_Man.encontrar_proximo_indice(streamlit.dataframe_sla, streamlit.fim_op)
        )
    streamlit.demanda_acumulada.set_demanda(acumulo_atualizado)