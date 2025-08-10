import json
import pandas as pd
from datetime import datetime

def save(file_path, **dataframes):
    """
    Salva múltiplos DataFrames em um arquivo JSON
    
    Uso:
    save_multiple_dfs_to_json("dados.json",
        analistas=df1,
        clientes=df2,
        metricas=df3)
    """
    serialized_data = {}
    
    for name, df in dataframes.items():
        # Converte DataFrame para formato serializável
        serialized_data[name] = {
            "columns": df.columns.tolist(),
            "data": df.values.tolist()
        }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(serialized_data, f, ensure_ascii=False, indent=4)
        
def load(file_path):
    """Carrega múltiplos DataFrames de um arquivo JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dfs = {}
    
    for name, df_data in data.items():
        # Reconstrói o DataFrame
        dfs[name] = pd.DataFrame(
            data=df_data["data"],
            columns=df_data["columns"]
        )
    
    return dfs