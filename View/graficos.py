# Módulo de visualização gráfica usando Plotly e Streamlit
import pandas as pd
import plotly.graph_objects as go  # Biblioteca para criação de gráficos interativos
import streamlit as st  # Framework para criação de aplicações web
import numpy as np
from scipy.stats import gaussian_kde

def draw_grafico_demanda_capacidade(key: str):  
    """
    Cria e exibe um gráfico comparando demanda (derivação) vs capacidade (produção)
    
    Parâmetros:
        key (str): Identificador único para o componente no Streamlit (evita recriação)
    
    Fluxo:
        1. Cria figura base do Plotly
        2. Adiciona linha de demanda (derivação) com estilo específico
        3. Adiciona linha de capacidade (produção) com estilo diferenciado
        4. Configura eixos e layout
        5. Renderiza o gráfico no Streamlit
    """
    
    # Inicializa a figura do Plotly
    fig = go.Figure()
    
    # Linha 1: Demanda (Derivação) - Entrada de trabalho
    fig.add_scatter(
        x=st.session_state.df_derivacao['horario'],  # Eixo X: Horários do dia
        y=st.session_state.df_derivacao['quantidade'],  # Eixo Y: Volume de trabalho
        mode='lines+markers',  # Combinação de linhas e marcadores
        name='Derivação',  # Legenda
        line=dict(
            color='tomato',  # Cor azul claro para demanda
            width=2,  # Espessura da linha
            shape='hv'  # Formato em degraus (horizontal-vertical)
        )
    )
    
    # Linha 2: Capacidade (Produção) - Saída processada
    fig.add_scatter(
        x=st.session_state.df_producao['horario'],  # Mesmo eixo X (horários)
        y=st.session_state.df_producao['quantidade'],  # Volume processado
        mode='lines+markers',
        name='Produção',  # Legenda diferenciada
        line=dict(
            color='royalblue',  # Cor violeta para capacidade
            width=2,
            shape='hv'  # Formato em degraus
        )
    )
    
    # Linha fantasma: Mantém a escala do eixo Y mesmo com acumulo zero
    fig.add_scatter(
        line=dict(width=0)  # Linha invisível
    )
    
    # Configurações gerais do layout do gráfico
    fig.update_layout(
        xaxis=dict(
            range=st.session_state.time_range,
            tickangle=45,  # Labels inclinados
            tickformat='%H:%M',
        )
    )
        
    # Renderiza o gráfico no Streamlit usando a chave única
    st.plotly_chart(fig, key=key)
    

def draw_grafico_acumulo(key: str):
    """
    Cria e exibe um gráfico de acumulação de trabalho
    
    Parâmetros:
        key (str): Identificador único para o componente no Streamlit
    
    Fluxo:
        1. Cria figura base
        2. Adiciona linha de acumulação com estilo destacado
        3. Adiciona linha invisível para manter escala
        4. Configura eixos
        5. Renderiza o gráfico
    """
    
    fig = go.Figure()
    
    # Linha principal: Acumulação de trabalho pendente
    fig.add_scatter(
        x=st.session_state.df_acumulo['horario'],  # Eixo X: Horários
        y=st.session_state.df_acumulo['quantidade'],  # Eixo Y: Trabalho acumulado
        mode='lines+markers',
        name='Acumulo',  # Legenda
        line=dict(
            color='gold',  # Cor gold para destaque
            width=2,
            shape='hv'  # Formato em degraus
        )
    )
    
    # Linha 2: Capacidade (Produção) - Saída processada
    fig.add_scatter(
        x=st.session_state.df_acumulo['horario'],  # Mesmo eixo X (horários)
        y=st.session_state.df_acumulo['quantidade'],  # Volume processado
        mode='lines',
        name='Produção',  # Legenda diferenciada
        line=dict( 
            color='blue',  # Cor violeta para capacidade
            width=0,
            shape='hv'  # Formato em degraus
        ),
        showlegend=False  # Adicione esta linha para ocultar da legenda
    )
    
    # Linha fantasma: Mantém a escala do eixo Y mesmo com acumulo zero
    fig.add_scatter(
        line=dict(width=0)  # Linha invisível
    )

    # Configurações de layout
    fig.update_layout(
        xaxis=dict(
            # range=st.session_state.time_range,  # Mesmo range temporal
            range=st.session_state.time_range,
            tickangle=45,  # Labels inclinados
            tickformat='%H:%M',
        )
    )
        
    # Renderização no Streamlit
    st.plotly_chart(fig, key=key)
    
    
def draw_hist_dist(dataframe, key, color, title):
    """
    color 1 = portland
    color 2 = bupu
    """
    if color == 1:
        color = 'portland'
    elif color == 2:
        color = 'bupu'
        
    fig = go.Figure(go.Bar(
        x=dataframe['horario'],
        y=dataframe['quantidade'],
        marker=dict(
            color=dataframe['quantidade'],  # Cor baseada na altura
            colorscale=color,
            colorbar=dict(title='')
        )
    ))
    
    # Linha fantasma: Mantém a escala do eixo Y mesmo com acumulo zero
    fig.add_scatter(
        line=dict(width=0)  # Linha invisível
    )

    fig.update_layout(
        title=title,
        bargap=0.001,
        xaxis=dict(
            range=[int(st.session_state.time_range[0]), int(st.session_state.time_range[1])],
            tickangle=45,  # Labels inclinados
            tickformat='%H:%M',
        )
    )
        
    st.plotly_chart(fig, key=key)