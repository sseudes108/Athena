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
            st.session_state.tma = st.number_input(label="TMA - Segundos", value=156, step=1, key="tma_input")
            
        with sla_col:
            st.session_state.sla = st.number_input(label="SLA - Minutos", step=1, key="sla_input")
            
        with inicio_col:
            st.session_state.inicio_op = st.selectbox(label="Inicio Operacao", options=["07:00", "08:00"], key="inicio_op_input")
            
        with fim_col:
            st.session_state.fim_op = st.selectbox(label="Final Operacao", options=["22:00", "21:00"], key="fim_op_input")
            
        with upload_col:
            uploaded_file = st.file_uploader(label="CSV")
            st.session_state.time_range = Data_Man.get_range(st.session_state.inicio_op, st.session_state.fim_op)
            
            if uploaded_file is None:
                st.session_state.df_derivacao = Data_Man.get_dataframe_vazio()
                st.session_state.df_producao = Data_Man.get_dataframe_vazio()
                st.session_state.df_acumulo = Data_Man.get_dataframe_vazio()
                
            else:
                # if not athena:
                st.session_state.df_csv = Data_Man.get_dataframe(uploaded_file)                
                st.session_state.calculadora = Calculadora()
                                
                (st.session_state.demanda_atual, 
                 st.session_state.demanda_acumulada, 
                 st.session_state.capacidade_operacional) = st.session_state.calculadora.create_instancias()
                
                st.session_state.demanda_inicial = st.session_state.df_csv['quantidade'].tolist()
                st.session_state.demanda_atual.set_demanda(st.session_state.demanda_inicial)
                
                st.session_state.acumulo_inicial = st.session_state.calculadora.calcular_acumulo(st.session_state.demanda_inicial)
                st.session_state.demanda_acumulada.set_demanda(st.session_state.acumulo_inicial)
                
                st.session_state.analistas_lista = st.session_state.calculadora.athena(
                    st.session_state.tma, 
                    st.session_state.demanda_atual, 
                    st.session_state.demanda_acumulada, 
                    st.session_state.capacidade_operacional
                )

                #Criação dos dataframes para a plotagem dos graficos
                st.session_state.df_derivacao = st.session_state.df_csv 
                st.session_state.df_producao = Data_Man.get_custom_dataframe(st.session_state.capacidade_operacional.get_capacidade_producao())
                st.session_state.df_acumulo = Data_Man.get_custom_dataframe(st.session_state.demanda_acumulada.get_demanda())
            
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
                Graficos.draw_grafico_demanda_capacidade('du_cap_vazio')

            with acum_col:
                Graficos.draw_grafico('du_acum_vazio')
                                
        with sab_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                Graficos.draw_grafico_demanda_capacidade('sab_cap_vazio')
            
            with acum_col:
                Graficos.draw_grafico('sab_acum_vazio')
                
            
        with dom_tab:
            der_cap_col, acum_col = st.columns([1,1])
            
            with der_cap_col:
                Graficos.draw_grafico_demanda_capacidade('dom_cap')

            with acum_col:
                Graficos.draw_grafico('dom_acum')
        
    with st.container(): # Tabela
        if uploaded_file is None:
            st.caption(f"Analistas - {0}")
            pass
        else:
            st.caption(f"Analistas - {len(st.session_state.analistas_lista)}")
            analistas_agrupados = Data_Man.get_analistas_agrupados(st.session_state.analistas_lista)
            
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
                        st.write(f"{st.session_state.analistas_lista[analista].get_horarios()[0]}")
                        
                    with almoco_col:
                        st.caption("Almoco")
                        st.write(f"{st.session_state.analistas_lista[analista].get_horarios()[1]}")
                        
                    with saida_col:
                        st.caption("Saida")
                        st.write(f"{st.session_state.analistas_lista[analista].get_horarios()[2]}")
                st.divider()

def main():
    draw_page()

if __name__ == '__main__':
    main()