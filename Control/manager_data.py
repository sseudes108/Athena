import pandas as pd

def get_dataframe_vazio():
    horarios = [f"{h:02d}:00" for h in range(0, 24)]
    quantidades = [0] * 24

    df = pd.DataFrame({
        'horario': horarios,
        'quantidade': quantidades
    })
    
    return df

def get_dataframe(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df

def get_custom_dataframe(quantidade):
    horarios = [f"{h:02d}:00" for h in range(24)]
    df = pd.DataFrame({
        'horario': horarios,
        'quantidade': quantidade
    })
    return df
    

def get_range(inicio_op:str, fim_op:str):
    hora_inicio = inicio_op.split(':')[0]
    hora_fim = fim_op.split(':')[0]
    return [int(hora_inicio), int(hora_fim)-1]

def get_analistas_agrupados(analistas):
    dados = []
    for analista in analistas:
        horario_entrada = analista.get_horarios()[0]
        dados.append(horario_entrada)
        
    df = pd.DataFrame(dados, columns=['horario'])
    df_agrupado = df.groupby('horario').size().reset_index(name='quantidade')
    return df_agrupado

def main():
    pass

if __name__ == '__main__':
    main()