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
            
        # Calcula a capacidade de produção ao instanciar o objeto
        self.set_capacidade_producao()
        
    # Retorna a lista de horários (entrada, almoço, saída)
    def get_horarios(self):
        return [self.entrada, self.almoco, self.saida]
                
    # def str_to_time(self, hora_str):
    #     return datetime.strptime(hora_str, "%H:%M")

    def set_capacidade_producao(self):
        # Função helper para normalização
        def normalize_dt(dt):
            return datetime(2000, 1, 1, dt.hour, dt.minute, dt.second)
        
        df_sla = st.session_state.dataframe_sla.reset_index(drop=True)
        
        # Normaliza todos os horários para 2000-01-01
        entrada_dt = normalize_dt(self.entrada)
        almoco_inicio_dt = normalize_dt(self.almoco)
        almoco_fim_dt = normalize_dt(self.almoco) + timedelta(minutes=60)
        saida_dt = normalize_dt(self.saida)

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

                # CORREÇÃO: Converta para minutos
                minutos_validos = trabalho_total.total_seconds() / 60 - pausa.total_seconds() / 60
                minutos_trabalhados = max(0, min(minutos_validos, st.session_state.sla))

            tempo_trabalhado.append(minutos_trabalhados)
                    
        # Agora calcula capacidade
        capacidade = [floor(mins * 60 / self.tma) for mins in tempo_trabalhado]
        # print(f"Tipo de hora_inicio: {type(hora_inicio)}")
        # print(f"Tipo de entrada_dt: {type(entrada_dt)}")
        # print(f"Diferença: {saida_dt - entrada_dt}")
                
        self.capacidade_producao = capacidade
        
        
    # def set_capacidade_producao(self):
    #     df_sla = st.session_state.dataframe_sla.reset_index(drop=True)
        
    #     almoco_duracao = 60  # minutos
        
    #     entrada_dt = self.entrada
    #     almoco_inicio_dt = self.almoco
    #     almoco_fim_dt = almoco_inicio_dt + timedelta(minutes=almoco_duracao)
    #     saida_dt = self.saida

    #     tempo_trabalhado = []
        
    #     for i in range(len(df_sla)):
    #         # CORREÇÃO: Não converta para string, mantenha como datetime
    #         hora_inicio = df_sla.loc[i, 'horario']
            
    #         if i < len(df_sla) - 1:
    #             hora_fim = df_sla.loc[i + 1, 'horario']
    #         else:
    #             # CORREÇÃO: Use o último horário + SLA
    #             hora_fim = hora_inicio + timedelta(minutes=st.session_state.sla)

    #         minutos_trabalhados = 0

    #         # Interseção com jornada total
    #         trabalho_inicio = max(hora_inicio, entrada_dt)
    #         trabalho_fim = min(hora_fim, saida_dt)

    #         if trabalho_fim > trabalho_inicio:
    #             trabalho_total = trabalho_fim - trabalho_inicio

    #             # Subtrai interseção com o almoço
    #             pausa_inicio = max(trabalho_inicio, almoco_inicio_dt)
    #             pausa_fim = min(trabalho_fim, almoco_fim_dt)

    #             if pausa_fim > pausa_inicio:
    #                 pausa = pausa_fim - pausa_inicio
    #             else:
    #                 pausa = timedelta(minutes=0)

    #             # CORREÇÃO: Converta para minutos
    #             minutos_validos = trabalho_total.total_seconds() / 60 - pausa.total_seconds() / 60
    #             minutos_trabalhados = max(0, min(minutos_validos, st.session_state.sla))

    #         tempo_trabalhado.append(minutos_trabalhados)
                    
    #     # Agora calcula capacidade
    #     capacidade = [floor(mins * 60 / self.tma) for mins in tempo_trabalhado]
    #     print(f"Tipo de hora_inicio: {type(hora_inicio)}")
    #     print(f"Tipo de entrada_dt: {type(entrada_dt)}")
    #     print(f"Diferença: {saida_dt - entrada_dt}")
                
    #     self.capacidade_producao = capacidade

    # Retorna a lista de capacidade de produção por hora
    def get_capacidade_producao(self):
        return self.capacidade_producao