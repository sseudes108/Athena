import pandas as pd  # Biblioteca para manipulação de dados em DataFrame

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
    horarios = [f"{h:02d}:00" for h in range(24)]
    
    # Cria DataFrame com valores personalizados
    df = pd.DataFrame({
        'horario': horarios,
        'quantidade': quantidade
    })
    return df
    

def get_range(inicio_op:str, fim_op:str):
    """
    Calcula o range horário operacional como intervalo numérico
    
    Parâmetros:
        inicio_op: String no formato "HH:MM" (ex: "08:00")
        fim_op: String no formato "HH:MM" (ex: "18:00")
        
    Retorna:
        Lista com [hora_inicio, hora_fim-1] (intervalo fechado-início, aberto-fim)
        Ex: ["08:00", "18:00"] → [8, 17]
    """
    # Extrai componente hora das strings
    hora_inicio = inicio_op.split(':')[0]
    hora_fim = fim_op.split(':')[0]
    
    # Converte para inteiros e ajusta limite superior
    return [int(hora_inicio), int(hora_fim)-1]

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
    dados = []
    # Coleta horários de entrada de todos os analistas
    for analista in analistas:
        horario_entrada = analista.get_horarios()[0]  # Primeiro horário é entrada
        dados.append(horario_entrada)
        
    # Cria DataFrame temporário
    df = pd.DataFrame(dados, columns=['horario'])
    
    # Agrupa por horário e conta ocorrências
    df_agrupado = df.groupby('horario').size().reset_index(name='quantidade')
    
    return df_agrupado