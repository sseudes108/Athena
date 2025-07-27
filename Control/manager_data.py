from datetime import datetime, timedelta
import pandas as pd  # Biblioteca para manipulação de dados em DataFrame
import streamlit as st

def get_dataframe_vazio():
    """
    Cria um DataFrame vazio com estrutura padrão (24 horas)
    
    Retorna:
        DataFrame com colunas:
          'horario': strings no formato "HH:00" para 24 horas
          'quantidade': zeros para todas as horas
    """
    # Gera lista de horários: ["00:00", "01:00", ..., "23:00"]
    horarios = [f"{h:02d}:00" for h in range(0, 24)]
    
    # Lista de 24 zeros
    quantidades = [0] * 24

    # Cria DataFrame estruturado
    df = pd.DataFrame({
        'horario': horarios,
        'quantidade': quantidades
    })
    
    return df

def get_dataframe(uploaded_file):
    """
    Lê um arquivo CSV carregado pelo usuário e retorna como DataFrame
    
    Parâmetros:
        uploaded_file: Objeto de arquivo carregado via Streamlit
        
    Retorna:
        DataFrame com os dados do CSV
    """
    df = pd.read_csv(uploaded_file)
    return df

def get_custom_dataframe(quantidade):
    """
    Cria DataFrame customizado com valores de quantidade fornecidos
    
    Parâmetros:
        quantidade: Lista de 24 valores numéricos
        
    Retorna:
        DataFrame com estrutura:
          'horario': horas formatadas ("00:00" a "23:00")
          'quantidade': valores do parâmetro de entrada
    """
    # Gera lista de horários padrão
    horarios = []
    for hora in range(24):
        for minuto in range(0, 60, st.session_state.sla):
            horarios.append(f"{hora:02d}:{minuto:02d}")
    
    # Cria DataFrame com valores personalizados
    df = pd.DataFrame({
        'horario': horarios,
        'quantidade': quantidade
    })
    
    return df

def get_range(dataframe, inicio_op:str, fim_op:str):
    """
    Calcula o range horário operacional como intervalo numérico
    
    Parâmetros:
        inicio_op: String no formato "HH:MM" (ex: "08:00")
        fim_op: String no formato "HH:MM" (ex: "18:00")
        
    Retorna:
        Lista com [hora_inicio, hora_fim-1] (intervalo fechado-início, aberto-fim)
        Ex: ["08:00", "18:00"] → [8, 17]
    """
    hora_inicio_index = encontrar_indice_por_horario(dataframe, inicio_op)
    hora_fim_index = encontrar_indice_por_horario(dataframe, fim_op)
    return[hora_inicio_index, hora_fim_index]

def encontrar_indice_por_horario(df:pd.DataFrame, horario_alvo):
    """
    Encontra o índice da linha onde a hora (sem data) é igual ao horário alvo.
    Aceita `str` (ex: '10:00') ou `datetime.time`
    """

    if isinstance(horario_alvo, str):
        horario_alvo = datetime.strptime(horario_alvo, "%H:%M").time()
    
    matches = df.index[df['horario'].dt.time == horario_alvo].tolist()

    if matches:
        return matches[0]
    else:
        return None

def converte_blocos_para_tempo(df):
    df = df.copy()
    def str_to_datetime(time_str):
        try:
            # Converte diretamente a string "HH:MM" para datetime
            time_str = str(time_str)
            return datetime.strptime(time_str, "%H:%M")
        except ValueError:
            # Caso o formato esteja incorreto
            return datetime(2000, 1, 1)  # Valor padrão
    
    df['horario'] = df['horario'].apply(str_to_datetime)
    return df

def get_dataframe_sla(dataframe_original, sla):
    # Garante que a coluna 'horario' esteja no formato datetime
    dataframe_original = dataframe_original.copy()
    dataframe_original['horario'] = pd.to_datetime(dataframe_original['horario'], format="%H:%M")

    # Adiciona coluna auxiliar 'hora_base' para merge
    dataframe_original['hora_base'] = dataframe_original['horario'].dt.strftime('%H:%M')

    # Gera todos os horários de blocos por SLA
    horarios = []
    for hora in range(24):
        for minuto in range(0, 60, sla):
            horarios.append(f"{hora:02d}:{minuto:02d}")

    df_intervalo = pd.DataFrame({'horario': horarios})
    df_intervalo['hora_base'] = df_intervalo['horario'].str[:2] + ':00'

    # Faz merge com o DataFrame original para importar as quantidades
    df_merged = pd.merge(df_intervalo, dataframe_original, on='hora_base', suffixes=('', '_hora'))

    # Distribui proporcionalmente
    if 60 % sla == 0:
        proporcao = sla / 60
        df_merged['quantidade'] = df_merged['quantidade'] * proporcao
    else:
        intervalos_por_hora = df_merged.groupby('hora_base')['horario'].transform('count')
        df_merged['quantidade'] = df_merged['quantidade'] / intervalos_por_hora

    # Seleciona colunas finais
    df_final = df_merged[['horario', 'quantidade']]
    
    return df_final

def get_analistas_agrupados(analistas):
    """
    Agrupa analistas por horário de entrada
    
    Parâmetros:
        analistas: Lista de objetos Analista
        
    Retorna:
        DataFrame agrupado com colunas:
          'horario': horário de entrada
          'quantidade': contagem de analistas por horário
    """
    # Coleta todos os horários
    horarios = [analista.get_horarios() for analista in analistas]
    
    # Cria DataFrame com todas as colunas
    df = pd.DataFrame(horarios, columns=['entrada', 'almoco', 'saida', 'carga_horaria'])
    
    # Agrupa por todos os horários
    df_agrupado = df.groupby(['entrada', 'almoco', 'saida']).agg(
        quantidade=('entrada', 'size'),
        carga_horaria=('carga_horaria', 'first')
    ).reset_index()
    
    return df_agrupado

def formatar_timedelta_para_hora_minuto(td: timedelta) -> str:
    total_minutos = int(td.total_seconds() // 60)
    horas = total_minutos // 60
    minutos = total_minutos % 60
    return f"{horas:02d}:{minutos:02d}"