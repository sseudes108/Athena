# Módulo de visualização gráfica usando Plotly e Streamlit
import plotly.graph_objects as go  # Biblioteca para criação de gráficos interativos
import streamlit as st  # Framework para criação de aplicações web

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
            color='skyblue',  # Cor azul claro para demanda
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
            color='violet',  # Cor violeta para capacidade
            width=2,
            shape='hv'  # Formato em degraus
        )
    )
    
    # Configurações gerais do layout do gráfico
    fig.update_layout(
        xaxis=dict(
            range=st.session_state.time_range,  # Faixa horária definida pelo usuário
            tickangle=45  # Ângulo de exibição dos labels (melhor legibilidade)
        )
    )
        
    # Renderiza o gráfico no Streamlit usando a chave única
    st.plotly_chart(fig, key=key)

def draw_grafico(key: str):
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
            color='salmon',  # Cor salmão para destaque
            width=2,
            shape='hv'  # Formato em degraus
        )
    )
    
    # Linha fantasma: Mantém a escala do eixo Y mesmo com acumulo zero
    fig.add_scatter(
        line=dict(width=0)  # Linha invisível
    )
    
    # Configurações de layout
    fig.update_layout(
        xaxis=dict(
            range=st.session_state.time_range,  # Mesmo range temporal
            tickangle=45  # Labels inclinados
        )
    )
        
    # Renderização no Streamlit
    st.plotly_chart(fig, key=key)

def main():
    """Função vazia para execução isolada (não utilizada no contexto principal)"""
    pass

if __name__ == '__main__':
    # Ponto de entrada para testes isolados (não usado na aplicação principal)
    main()