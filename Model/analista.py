from datetime import datetime, timedelta
from math import floor  # Importa a função floor para arredondamento para baixo
import streamlit as st

# Classe que representa um analista com horários definidos e capacidade de produção por hora
class Analista():
    def __init__(self, tma, entrada: str, almoco: str, saida: str):
        # Lista com 24 posições, uma para cada hora do dia, inicializada com 0
        self.capacidade_producao = [0] * len(st.session_state.demanda_inicial)
        
        # Tempo médio de atendimento (TMA) em segundos
        self.tma = tma

        # Horários recebidos em formato string: "HH:MM"
        self.entrada = datetime.strptime(entrada, "%H:%M")
        self.almoco = datetime.strptime(almoco, "%H:%M")
        self.saida = datetime.strptime(saida, "%H:%M")
        self.carga_horaria = 0
            
        # Calcula a capacidade de produção ao instanciar o objeto
        self.set_capacidade_operacao()
        
    # Retorna a lista de horários (entrada, almoço, saída)
    def get_horarios(self):
        return [self.entrada, self.almoco, self.saida, self.carga_horaria]
                    
    def set_capacidade_operacao(self):
        df_sla = st.session_state.dataframe_sla.reset_index(drop=True)
        
        almoco_duracao = 60
        
        entrada_dt = self.entrada
        almoco_inicio_dt = self.almoco
        almoco_fim_dt = almoco_inicio_dt + timedelta(minutes=almoco_duracao)
        saida_dt = self.saida

        tempo_trabalhado = []
        
        for i in range(len(df_sla)):
            hora_inicio = df_sla.loc[i, 'horario']
            
            if i < len(df_sla) - 1:
                hora_fim = df_sla.loc[i + 1, 'horario']
            else:
                hora_fim = hora_inicio + timedelta(minutes=st.session_state.sla)

            minutos_trabalhados = 0

            # Interseção com jornada total
            trabalho_inicio = max(hora_inicio, entrada_dt)
            trabalho_fim = min(hora_fim, saida_dt)

            if trabalho_fim > trabalho_inicio:
                trabalho_total = trabalho_fim - trabalho_inicio

                # Subtrai interseção com o almoço
                pausa_inicio = max(trabalho_inicio, almoco_inicio_dt)
                pausa_fim = min(trabalho_fim, almoco_fim_dt)

                if pausa_fim > pausa_inicio:
                    pausa = pausa_fim - pausa_inicio
                else:
                    pausa = timedelta(minutes=0)

                minutos_validos = int((trabalho_total - pausa).seconds / 60)
                minutos_trabalhados = min(minutos_validos, int((hora_fim - hora_inicio).seconds / 60))

            tempo_trabalhado.append(minutos_trabalhados)
                    
        # Agora calcula capacidade
        capacidade = [round(mins * 60 / st.session_state.tma, 2) for mins in tempo_trabalhado]
        self.capacidade_producao = capacidade
        
        carga_horaria = (saida_dt - timedelta(hours=1)) - entrada_dt
        if carga_horaria == timedelta(hours=1):
            carga_horaria = timedelta(hours=2)

        self.carga_horaria = carga_horaria

    # Retorna a lista de capacidade de produção por hora
    def get_capacidade_operacao(self):
        return self.capacidade_producao