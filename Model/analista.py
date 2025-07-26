from math import floor  # Importa a função floor para arredondamento para baixo

# Classe que representa um analista com horários definidos e capacidade de produção por hora
class Analista():
    def __init__(self, tma, entrada: str, almoco: str, saida: str):
        # Lista com 24 posições, uma para cada hora do dia, inicializada com 0
        self.capacidade_producao = [0] * 24
        
        # Tempo médio de atendimento (TMA) em segundos
        self.tma = tma

        # Horários recebidos em formato string: "HH:MM"
        self.entrada: str = entrada
        self.almoco: str = almoco
        self.saida: str = saida
        
        # Calcula a capacidade de produção ao instanciar o objeto
        self.set_capacidade_producao()
        
    # Retorna a lista de horários (entrada, almoço, saída)
    def get_horarios(self):
        return [self.entrada, self.almoco, self.saida]
        
    # Calcula a capacidade de produção por hora com base no tempo trabalhado e TMA
    def set_capacidade_producao(self):
        tempo_trabalhado = [0] * 24  # Inicializa o vetor de tempo trabalhado por hora

        # Converte horários de string para horas e minutos (inteiros)
        entrada_hora = int(self.entrada.split(':')[0])
        entrada_minutos = int(self.entrada.split(':')[1])

        almoco_hora = int(self.almoco.split(':')[0])
        almoco_minutos = int(self.almoco.split(':')[1])

        saida_hora = int(self.saida.split(':')[0])
        saida_minutos = int(self.saida.split(':')[1])
        
        # Preenche o tempo antes da entrada com 0 minutos trabalhados
        hora = 0
        while hora < entrada_hora:
            tempo_trabalhado[hora] = 0
            hora += 1
        
        # Calcula minutos trabalhados na hora de entrada
        tempo_trabalhado[hora] = 60 - entrada_minutos
        
        # Preenche as horas completas entre entrada e almoço com 60 minutos
        while hora < almoco_hora:
            tempo_trabalhado[hora] = 60
            hora += 1
        
        # Hora do almoço — desconta tempo se houver minutos no horário de almoço
        if almoco_minutos > 0:
            tempo_trabalhado[hora] = almoco_minutos  # Tempo trabalhado antes do almoço
            hora += 1
            tempo_trabalhado[hora] = 60 - almoco_minutos  # Tempo após o almoço
        else:
            tempo_trabalhado[hora] = 0  # Hora completamente de almoço
            hora += 1
        
        # Horas completas entre fim do almoço e saída
        while hora < saida_hora:
            tempo_trabalhado[hora] = 60
            hora += 1
            
        # Processa a última hora se saída não for em hora cheia
        if saida_minutos > 0:
            tempo_trabalhado[hora] = saida_minutos  # Minutos trabalhados na última hora
            hora += 1
            tempo_trabalhado[hora] = 0  # Após saída não há trabalho

        # Horas restantes até meia-noite são não trabalhadas
        while hora < 24:
            tempo_trabalhado[hora] = 0
            hora += 1
        
        # Calcula a capacidade de produção por hora com base nos minutos trabalhados
        capacidade = [0] * 24
        for i in range(24):
            # Cada unidade representa quantos atendimentos cabem naquela hora
            prop_hora = floor((tempo_trabalhado[i] * 60) / self.tma)
            capacidade[i] = prop_hora
            
        # Atribui a capacidade de produção final
        self.capacidade_producao = capacidade
            
    # Retorna a lista de capacidade de produção por hora
    def get_capacidade_producao(self):
        return self.capacidade_producao