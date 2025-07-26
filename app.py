import streamlit as st

from View import layout as Layout
from View import graficos as Graficos

from Control import manager_data as Data_Man
from Control.calculadora import Calculadora

def draw_page():
    Layout.set_config_title() # Title, icon page, wide layout, css
    
    with st.container(): # Inputs
        st.caption("Inputs")
        tma_col, sla_col, inicio_col, fim_col, upload_col = st.columns([1,1,1,1,1])
        
        with tma_col:
            tma = st.number_input(label="TMA - Segundos", value=156, step=1, key="tma_input")
            
        with sla_col:
            sla = st.number_input(label="SLA - Minutos", step=1, key="sla_input")
            
        with inicio_col:
            inicio_op = st.selectbox(label="Inicio Operacao", options=["07:00", "08:00"], key="inicio_op_input")
            
        with fim_col:
            fim_op = st.selectbox(label="Final Operacao", options=["22:00", "21:00"], key="fim_op_input")
            
        with upload_col:
            uploaded_file = st.file_uploader(label="CSV")
            time_range = Data_Man.get_range(inicio_op, fim_op)
            
            if uploaded_file is None:
                df_derivacao = Data_Man.get_dataframe_vazio()
                df_producao = Data_Man.get_dataframe_vazio()
                df_acumulo = Data_Man.get_dataframe_vazio()
                
            else:
                # if not athena:
                df_csv = Data_Man.get_dataframe(uploaded_file)                
                calculadora = Calculadora()
                                
                (demanda_atual, 
                 demanda_acumulada, 
                 capacidade_operacional) = calculadora.create_instancias()
                
                demanda_inicial = df_csv['quantidade'].tolist()
                demanda_atual.set_demanda(demanda_inicial)
                
                acumulo_inicial = calculadora.calcular_acumulo(demanda_inicial)
                demanda_acumulada.set_demanda(acumulo_inicial)
                
                analistas_lista = calculadora.athena(
                    tma, 
                    demanda_atual, 
                    demanda_acumulada, 
                    capacidade_operacional
                )

                #Criação dos dataframes para a plotagem dos graficos
                df_derivacao = df_csv 
                df_producao = Data_Man.get_custom_dataframe(capacidade_operacional.get_capacidade_producao())
                df_acumulo = Data_Man.get_custom_dataframe(demanda_acumulada.get_demanda())
            
                # if athena
                
    with st.container(): # Graficos
        st.caption("Graficos")
        du_tab, sab_tab, dom_tab = st.tabs([
            "Dia Util",
            "Sabado",
            "Domingo"
        ])
        
        with du_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                Graficos.draw_grafico_demanda_capacidade(
                    df_derivacao, 
                    'skyblue', 
                    df_producao, 
                    'violet', 
                    time_range, 
                    'du_cap_vazio'
                )
            
            with acum_col:
                Graficos.draw_grafico(df_acumulo,'salmon', time_range, 'du_acum_vazio')
                                
        with sab_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                Graficos.draw_grafico_demanda_capacidade(
                    df_derivacao, 
                    'skyblue', 
                    df_producao, 
                    'violet', 
                    time_range,
                    'sab_cap_vazio'
                )
            
            with acum_col:
                Graficos.draw_grafico(df_acumulo,'salmon', time_range, 'sab_acum_vazio')
                
            
        with dom_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                Graficos.draw_grafico_demanda_capacidade(
                    df_derivacao, 
                    'skyblue', 
                    df_producao, 
                    'violet', 
                    time_range,
                    'dom_cap'
                )

            with acum_col:
                Graficos.draw_grafico(df_acumulo,'salmon', time_range, 'dom_acum')
        
    with st.container(): # Tabela
        st.caption(f"Analistas - {len(analistas_lista)}")
        if uploaded_file is None:
            pass
        else:
            analistas_agrupados = Data_Man.get_analistas_agrupados(analistas_lista)
            
            for analista, row in analistas_agrupados.iterrows():
                with st.container():
                    buttons_col, contagem_col, entrada_col, almoco_col, saida_col = st.columns([1,1,1,1,1])
                    with buttons_col:
                        st.caption("Buttons Add Rem")
                        st.write("Buttons")
                        
                    with contagem_col:
                        st.caption("Quantidade")
                        st.write(f"{row['quantidade']}")
                        
                    with entrada_col:
                        st.caption("Entrada")
                        st.write(f"{analistas_lista[analista].get_horarios()[0]}")
                        
                    with almoco_col:
                        st.caption("Almoco")
                        st.write(f"{analistas_lista[analista].get_horarios()[1]}")
                        
                    with saida_col:
                        st.caption("Saida")
                        st.write(f"{analistas_lista[analista].get_horarios()[2]}")
                st.divider()

def main():
    draw_page()

if __name__ == '__main__':
    main()