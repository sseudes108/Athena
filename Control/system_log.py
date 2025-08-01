import json
import pandas as pd
from datetime import datetime
import os

def salvar_log(df, parametros, nome_arquivo='log_athena.json'):
    log = {
        "timestamp": datetime.now().isoformat(),
        "parametros": parametros,
        "dataframe": df.to_dict(orient="records")
    }
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"🔒 Log salvo em: {nome_arquivo}")