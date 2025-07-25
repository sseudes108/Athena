class Analista():
    def __init__(self, entrada:str, almoco:str, saida:str):
        self.capacidade_producao = [0] * 24
        self.entrada:str = entrada
        self.almoco:str = almoco
        self.saida:str = saida
        
        self.set_capacidade_producao()
        
    def set_capacidade_producao(self):
        capacidade = [0] * 24

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
            capacidade[hora] = 0
            print(f"{hora} - {capacidade[hora]}")
            hora = hora + 1
        
        capacidade[hora] = 60 - entrada_minutos
        print(f"{hora} - {capacidade[hora]}")
        
        #Almoço
        
        while hora < almoco_hora:
            capacidade[hora] = 60
            print(f"{hora} - {capacidade[hora]}")
            hora = hora + 1
        
        if almoco_minutos > 0:
            capacidade[hora] = 60 - (60 - almoco_minutos)
            print(f"{hora} - {capacidade[hora]}")
            
            hora = hora + 1
            
            capacidade[hora] = 60 - capacidade[hora - 1]
            print(f"{hora} - {capacidade[hora]}")
        else:
            capacidade[hora] = 0
            print(f"{hora} - {capacidade[hora]}")
            hora = hora + 1
            
        #Saida
        
        while hora < saida_hora:
            capacidade[hora] = 60
            print(f"{hora} - {capacidade[hora]}")
            hora = hora + 1
            
        if saida_minutos > 0:
            capacidade[hora] = 60 - (60 - saida_minutos)
            print(f"{hora} - {capacidade[hora]}")
            
            hora = hora + 1
            
            capacidade[hora] = 0
            print(f"{hora} - {capacidade[hora]}")
            
        while hora < 24:
            capacidade[hora]  = 0
            print(f"{hora} - {capacidade[hora]}")
            hora = hora + 1
            
    def get_capacidade_producao(self): return self.capacidade_producao

def main():
    pass
    # print("Analista 1")
    # print("")
    # analista = Analista("07:00","12:00","15:20")
    # print("Analista 2")
    # print("")
    # analista2 = Analista("07:40","12:30","17:45")
    # print("Analista 3")
    # print("")
    # analista3 = Analista("13:20","17:40","22:00")
    # # print(analista.get_capacidade_producao())
    # # print(analista2.get_capacidade_producao())
    # # print(analista3.get_capacidade_producao())

if __name__ == '__main__':
    main()