import plotly.graph_objects as go
import streamlit as st


def draw_grafico_demanda_capacidade(key):
    fig = go.Figure()
    
    fig.add_scatter(
        x=st.session_state.df_derivacao['horario'],
        y=st.session_state.df_derivacao['quantidade'],
        mode='lines+markers',
        name='Derivação',
        line=dict(
            color=f'skyblue',
            width=2,
            shape='hv'
        )
    )
    
    fig.add_scatter(
        x=st.session_state.df_producao['horario'],
        y=st.session_state.df_producao['quantidade'],
        mode='lines+markers',
        name='Produção',
        line=dict(
            color=f'violet',
            width=2,
            shape='hv'
        )
    )
    
    fig.update_layout(
        xaxis=dict(
            range=st.session_state.time_range,
            tickangle=45
        )
    )
        
    st.plotly_chart(fig, key=key)

def draw_grafico(key):
    fig = go.Figure()
    
    fig.add_scatter(
        x=st.session_state.df_acumulo['horario'],
        y=st.session_state.df_acumulo['quantidade'],
        mode='lines+markers',
        name='Acumulo',
        line=dict(
            color=f'salmon',
            width=2,
            shape='hv'
        )
    )
    
    fig.add_scatter(
        line=dict(
            width=0,
        )
    )
    
    fig.update_layout(
        xaxis=dict(
            range=st.session_state.time_range,
            tickangle=45
        )
    )
        
    st.plotly_chart(fig, key=key)

def main():
    pass

if __name__ == '__main__':
    main()