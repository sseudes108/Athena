import streamlit as st

from View import layout as Layout

def draw_page():
    Layout.set_config_title() # Title, icon page, wide layout, css
    
    with st.container(): # Inputs
        st.caption("Inputs")
        tma_col, sla_col, inicio_col, fim_col, upload_col = st.columns([1,1,1,1,1])
        
        with tma_col:
            tma = st.number_input(label="TMA - Segundos", step=1, key="tma_input")
            
        with sla_col:
            sla = st.number_input(label="SLA - Minutos", step=1, key="sla_input")
            
        with inicio_col:
            inicio_op = st.selectbox(label="Inicio Operacao", options=["07:00", "08:00"], key="inicio_op_input")
            
        with fim_col:
            fim_op = st.selectbox(label="Final Operacao", options=["21:00", "22:00"], key="fim_op_input")
            
        with upload_col:
            uploaded_file = st.file_uploader(label="CSV")
            
            if uploaded_file is None:
                pass
            else:
                pass
    
    with st.container(): # Graficos
        st.caption("Graficos")
        du_tab, sab_tab, dom_tab = st.tabs([
            "Dia Util",
            "Sabado",
            "Domingo"
        ])        
    with st.container(): # Tabela
        st.caption("Analistas")

def main():
    draw_page()

if __name__ == '__main__':
    main()