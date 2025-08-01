# Importações de bibliotecas
import streamlit as st  # Framework para criação de aplicações web
from functools import partial

# Importações de módulos internos
from Model.analista import Analista
from View import layout as Layout  # Módulo para configuração de layout
from View import graficos as Graficos  # Módulo para criação de gráficos
from Control import manager_data as Data_Man  # Gerenciador de dados
from Control.calculadora import Calculadora  # Lógica de cálculo de capacidade

def draw_page():
    """Função principal que renderiza toda a página da aplicação"""
    
    # Configuração inicial da página (título, ícone, layout, CSS)
    Layout.set_config_title()
    
    # Container 1: Área de inputs do usuário
    with st.container():
        st.caption("Inputs")
        # Cria 5 colunas com larguras iguais
        tma_col, sla_col, inicio_col, fim_col, upload_col = st.columns([1,1,1,1,1])
        
        # Coluna 1: Input para TMA (Tempo Médio de Atendimento)
        with tma_col:
            st.session_state.tma = st.number_input(
                label="TMA - Segundos", 
                value=156, 
                step=1, 
                key="tma_input"
            )
            
        # Coluna 2: Input para SLA (Service Level Agreement)
        with sla_col:
            st.session_state.sla = int(st.selectbox(
                label="SLA - Minutos",
                options=[
                    '15',
                    
                    '03',
                    '04',
                    '05',
                    '06',
                    '10',
                    '12',

                    '20',
                    '30',
                    '60'
                ],
                key="sla_input"
            ))

                        
        # Coluna 3: Seletor para horário de início das operações
        with inicio_col:
            st.session_state.inicio_op = st.selectbox(
                label="Inicio Operacao", 
                options=["07:00", "08:00"], 
                key="inicio_op_input"
            )
            
        # Coluna 4: Seletor para horário de término das operações
        with fim_col:
            st.session_state.fim_op = st.selectbox(
                label="Final Operacao", 
                options=["22:00", "21:00"], 
                key="fim_op_input"
            )
        
        # Verifica se a flag 'athena' existe no estado da sessão
        if 'athena' not in st.session_state:
            st.session_state.athena = False
            
        if 'tma_previo' not in st.session_state or st.session_state.tma_previo != st.session_state.tma:
            st.session_state.athena = False  # força recalcular
            st.session_state.tma_previo = st.session_state.tma
            
        if 'sla_previo' not in st.session_state or st.session_state.sla_previo != st.session_state.sla:
            st.session_state.athena = False  # força recalcular
            st.session_state.sla_previo = st.session_state.sla
            
        if 'inicio_op_previo' not in st.session_state or st.session_state.inicio_op_previo != st.session_state.inicio_op:
            st.session_state.athena = False  # força recalcular
            st.session_state.inicio_op_previo = st.session_state.inicio_op
            
        if 'fim_op_previo' not in st.session_state or st.session_state.fim_op_previo != st.session_state.fim_op:
            st.session_state.athena = False  # força recalcular
            st.session_state.fim_op_previo = st.session_state.fim_op
            
        if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file is not None:
            st.session_state.athena = False  # força recalcular
                    
        # Coluna 5: Upload de arquivo CSV com dados de produção
        with upload_col:
            uploaded_file = st.file_uploader(label="CSV")
        
            # Lógica para tratamento do arquivo carregado
            if uploaded_file is None:
                # Se nenhum arquivo foi carregado, inicializa dataframes vazios
                st.session_state.time_range = [st.session_state.inicio_op.split(':')[0], st.session_state.fim_op.split(':')[0]]
                st.session_state.df_derivacao = Data_Man.get_dataframe_vazio()
                st.session_state.df_producao = Data_Man.get_dataframe_vazio()
                st.session_state.df_acumulo = Data_Man.get_dataframe_vazio()
                
            else:                         
                # Fluxo para processamento inicial do arquivo
                if st.session_state.athena == False:
                   
                    # Carrega o CSV para um DataFrame
                    st.session_state.df_csv = Data_Man.get_dataframe(uploaded_file)
                    
                    # Inicializa a calculadora de capacidade
                    st.session_state.calculadora = Calculadora()
                                    
                    # Atualizada dataframe com base no SLA
                    st.session_state.dataframe_sla = Data_Man.get_dataframe_sla(st.session_state.df_csv, st.session_state.sla)
                    st.session_state.dataframe_sla = Data_Man.converte_blocos_para_tempo(st.session_state.dataframe_sla)
                    
                    # Calcula o range de tempo
                    st.session_state.time_range = Data_Man.get_range(
                        st.session_state.dataframe_sla,
                        st.session_state.inicio_op, 
                        st.session_state.fim_op
                    )
                                        
                    # Cria instâncias para gestão de dados
                    (st.session_state.demanda_atual, 
                    st.session_state.demanda_acumulada, 
                    st.session_state.capacidade_operacional) = st.session_state.calculadora.create_instancias()
                    
                    # Configura demanda inicial a partir do CSV
                    st.session_state.demanda_inicial = st.session_state.dataframe_sla['quantidade'].tolist()
                    st.session_state.demanda_atual.set_demanda(st.session_state.demanda_inicial)
                    
                    # Calcula acumulo inicial e configura instância
                    st.session_state.acumulo_inicial = st.session_state.calculadora.calcular_acumulo(st.session_state.demanda_inicial)
                    st.session_state.demanda_acumulada.set_demanda(st.session_state.acumulo_inicial)
                    
                    # Executa o algoritmo Athena para cálculo de capacidade
                    st.session_state.analistas_lista = st.session_state.calculadora.athena(
                        st.session_state.tma, 
                        st.session_state.demanda_atual, 
                        st.session_state.demanda_acumulada, 
                        st.session_state.capacidade_operacional
                    )

                    # Prepara DataFrames para visualização gráfica
                    st.session_state.df_derivacao = Data_Man.get_custom_dataframe(
                        st.session_state.dataframe_sla['quantidade'].tolist()
                    )
                    st.session_state.df_producao = Data_Man.get_custom_dataframe(
                        st.session_state.capacidade_operacional.get_capacidade_producao()
                    )
                    st.session_state.df_acumulo = Data_Man.get_custom_dataframe(
                        st.session_state.demanda_acumulada.get_demanda()
                    )
                    
                    print(st.session_state.capacidade_operacional.get_capacidade_producao())
                else:
                    st.session_state.df_derivacao = st.session_state.df_acumulo = Data_Man.get_custom_dataframe(
                        st.session_state.dataframe_sla['quantidade'].tolist()
                    )
                    
                    # atualizado ao adicionar ou remover analista, cada um tem uma logica diferente
                    st.session_state.df_producao = Data_Man.get_custom_dataframe(
                        st.session_state.capacidade_operacional.get_capacidade_producao()
                    )
                    
                    acumulo_atualizado = [a - b for a, b in zip(st.session_state.demanda_acumulada.get_demanda(), st.session_state.capacidade_operacional.get_capacidade_producao())]
                    acumulo_atualizado_sem_negativos = [max(0, v) for v in acumulo_atualizado]
                    st.session_state.demanda_acumulada.set_demanda(acumulo_atualizado_sem_negativos)
                    
                    st.session_state.df_acumulo = Data_Man.get_custom_dataframe(
                        st.session_state.acumulo_inicial
                    )
                    # st.session_state.df_acumulo = Data_Man.get_custom_dataframe(
                    #     st.session_state.demanda_acumulada.get_demanda()
                    # )
                
    # Container 2: Área de visualização de gráficos de demanda e acumulo
    with st.container():
        st.caption("Graficos")
        
        # Cria abas para diferentes dias da semana
        du_tab, sab_tab, dom_tab = st.tabs([
            "Dia Util",
            "Sabado",
            "Domingo"
        ])
        
        # Tab 1: Dias Úteis
        with du_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                # Gráfico de demanda vs capacidade
                Graficos.draw_grafico_demanda_capacidade('du_cap')

            with acum_col:
                # Gráfico de acumulação
                Graficos.draw_grafico_acumulo('du_acum')
                
            with st.container():
                hist_der_col, hist_acul_col = st.columns([1,1])
                with hist_der_col:
                    Graficos.draw_hist_dist(st.session_state.df_derivacao, 'der_dist_du', 1, 'Distribuição da Derivação Inicial')
                with hist_acul_col:
                    Graficos.draw_hist_dist(st.session_state.df_acumulo, 'aculm_dist_du', 2, 'Distribuição do Acumulo')
                                
        # Tab 2: Sábados
        with sab_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                Graficos.draw_grafico_demanda_capacidade('sab_cap')
            
            with acum_col:
                Graficos.draw_grafico_acumulo('sab_acum')
                
            with st.container():
                hist_der_col, hist_acul_col = st.columns([1,1])
                with hist_der_col:
                    Graficos.draw_hist_dist(st.session_state.df_derivacao, 'der_dist_sab', 1, 'Distribuição da Derivação Inicial')
                with hist_acul_col:
                    Graficos.draw_hist_dist(st.session_state.df_acumulo, 'aculm_dist_sab', 2, 'Distribuição do Acumulo')
                
        # Tab 3: Domingos
        with dom_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                Graficos.draw_grafico_demanda_capacidade('dom_cap')

            with acum_col:
                Graficos.draw_grafico_acumulo('dom_acum')
                
            with st.container():
                hist_der_col, hist_acul_col = st.columns([1,1])
                with hist_der_col:
                    Graficos.draw_hist_dist(st.session_state.df_derivacao, 'der_dist_dom', 1, 'Distribuição da Derivação Inicial')
                with hist_acul_col:
                    Graficos.draw_hist_dist(st.session_state.df_acumulo, 'aculm_dist_dom', 2, 'Distribuição do Acumulo')
        
    # Container 3: Área de exibição de resultados (tabela de analistas)
    with st.container():
        if uploaded_file is None:
            st.caption(f"Analistas - {0}")
        else:
            st.caption(f"Analistas - {len(st.session_state.analistas_lista)}")
            
            # Agrupa dados dos analistas para exibição
            len(f"{st.session_state.analistas_lista}")
            analistas_agrupados = Data_Man.get_analistas_agrupados(st.session_state.analistas_lista)
            
            for index, row in analistas_agrupados.iterrows():
                with st.container():
                    # Divisão em colunas para diferentes informações
                    buttons_col, contagem_col, horario_total_col, entrada_col, almoco_col, saida_col = st.columns([1,0.7,1,1,1,1])
                    
                    with buttons_col:
                        st.caption(" .")
                        add_bttn_col, rem_bttn_col = st.columns([1,1])
                        with add_bttn_col:
                            st.button(
                                label="➕ Add",
                                key=f'add_{index}',
                                on_click=partial(
                                    st.session_state.calculadora.add_analista,
                                    entrada=row['entrada'].strftime('%H:%M'),
                                    almoco=row['almoco'].strftime('%H:%M'),
                                    saida=row['saida'].strftime('%H:%M')
                                )
                            )
                        with rem_bttn_col:
                            st.button(
                                label="➖ Rem", 
                                key=f'rem_{index}',
                                on_click=partial(
                                    st.session_state.calculadora.rem_analista,
                                    entrada=row['entrada'].strftime('%H:%M'),
                                    almoco=row['almoco'].strftime('%H:%M'),
                                    saida=row['saida'].strftime('%H:%M')
                                )
                            )
                            
                    with contagem_col:
                        st.caption("Quantidade")
                        st.write(f"{row['quantidade']}")
                    
                    with horario_total_col:
                        st.caption("Carga Horaria")
                        horario_formatado = Data_Man.formatar_timedelta_para_hora_minuto(row['carga_horaria'])
                        st.write(horario_formatado)
                    
                    with entrada_col:
                        st.caption("Entrada")
                        horario_formatado = row['entrada'].strftime('%H:%M')
                        st.write(horario_formatado)
                    
                    with almoco_col:
                        st.caption("Almoco")
                        horario_formatado = row['almoco'].strftime('%H:%M')
                        st.write(horario_formatado)
                    
                    with saida_col:
                        st.caption("Saida")
                        horario_formatado = row['saida'].strftime('%H:%M')
                        st.write(horario_formatado)
                               
                st.divider()  # Separador visual entre analistas
            st.session_state.athena = True  # Ativa flag para evitar recálculos desnecessários

def main():
    """Função de entrada da aplicação"""
    draw_page()

if __name__ == '__main__':
    main()