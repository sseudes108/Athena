import plotly.graph_objects as go
import streamlit as st


def draw_grafico_demanda_capacidade(df_derivacao, color_der, df_producao, color_cap, range, key):
    fig = go.Figure()
    
    fig.add_scatter(
        x=df_derivacao['horario'],
        y=df_derivacao['quantidade'],
        mode='lines+markers',
        name='Derivação',
        line=dict(
            color=f'{color_der}',
            width=2,
            shape='hv'
        )
    )
    
    fig.add_scatter(
        x=df_producao['horario'],
        y=df_producao['quantidade'],
        mode='lines+markers',
        name='Produção',
        line=dict(
            color=f'{color_cap}',
            width=2,
            shape='hv'
        )
    )
    
    fig.update_layout(
        xaxis=dict(
            range=range,
            tickangle=45
        )
    )
        
    st.plotly_chart(fig, key=key)

def draw_grafico(dataframe, color, range, key):
    fig = go.Figure()
    
    fig.add_scatter(
        x=dataframe['horario'],
        y=dataframe['quantidade'],
        mode='lines+markers',
        name='Acumulo',
        line=dict(
            color=f'{color}',
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
            range=range,
            tickangle=45
        )
    )
        
    st.plotly_chart(fig, key=key)

def main():
    pass

if __name__ == '__main__':
    main()