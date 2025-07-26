from math import floor


class Analista():
    def __init__(self, tma, entrada:str, almoco:str, saida:str):
        self.capacidade_producao = [0] * 24
        self.tma = tma
        self.entrada:str = entrada
        self.almoco:str = almoco
        self.saida:str = saida
        
        self.set_capacidade_producao()
        
    def get_horarios(self): return [self.entrada, self.almoco, self.saida]
        
    def set_capacidade_producao(self):
        tempo_trabalhado = [0] * 24

        # Extrai hora e minuto de entrada, almoço, e saída
        entrada_hora = int(self.entrada.split(':')[0])
        entrada_minutos = int(self.entrada.split(':')[1])

        almoco_hora = int(self.almoco.split(':')[0])
        almoco_minutos = int(self.almoco.split(':')[1])

        saida_hora = int(self.saida.split(':')[0])
        saida_minutos = int(self.saida.split(':')[1])
        
        #Entrada
        
        hora = 0
        while hora < entrada_hora:
            tempo_trabalhado[hora] = 0
            hora = hora + 1
        
        tempo_trabalhado[hora] = 60 - entrada_minutos
        
        #Almoço
        
        while hora < almoco_hora:
            tempo_trabalhado[hora] = 60

            hora = hora + 1
        
        if almoco_minutos > 0:
            tempo_trabalhado[hora] = 60 - (60 - almoco_minutos)
            hora = hora + 1
            
            tempo_trabalhado[hora] = 60 - tempo_trabalhado[hora - 1]

        else:
            tempo_trabalhado[hora] = 0
            hora = hora + 1
            
        #Saida
        
        while hora < saida_hora:
            tempo_trabalhado[hora] = 60
            hora = hora + 1
            
        if saida_minutos > 0:
            tempo_trabalhado[hora] = 60 - (60 - saida_minutos)
            hora = hora + 1
            
            tempo_trabalhado[hora] = 0

        while hora < 24:
            tempo_trabalhado[hora]  = 0
            hora = hora + 1
        
        capacidade = [0] * 24
        for i in range(0, len(tempo_trabalhado)):
            prop_hora = floor((tempo_trabalhado[i] * 60) / self.tma)
            capacidade[i] = prop_hora
            
        self.capacidade_producao = capacidade
            
    def get_capacidade_producao(self): return self.capacidade_producao

def main():
    pass

if __name__ == '__main__':
    main()