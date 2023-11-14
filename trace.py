from droneposition import DronePosition

class Trace:
    #Gestisce la traccia di tutti i droni
    def __init__(self, 
                drones_number: int, 
                trace_check: int) -> None:
        self.__drones_number = drones_number
        self.__trace_quantity = 0
        self.__trace_position = []
        self.__trace_check = trace_check

    #Aggiunge ogni nuova posizione, aggiornando il contatore
    async def add_position(self, location: list) -> None:
        self.__trace_quantity += 1
        self.__trace_position.insert(0, location)

    #Ritorna la specifica posizione richiesta
    def get_position(self, pos_i, pos_j) -> list[int, int]:
        pos_index = self.__trace_position[pos_i]
        pos_complete = pos_index[pos_j]
        return pos_complete

    #Ritorna la lista specifica della posizioni di tutti i droni
    def get_every_position(self, pos_i) -> list[int]:
        pos_index = self.__trace_position[pos_i]
        return pos_index

    #Ritorna il numero di tracce interessate da controllare
    def get_trace_check(self) -> int:
        return self.__trace_check

    #Ritorna il numero di tracce interessate da controllare
    async def print_trace(self) -> None:
        for i in range(self.__trace_quantity):
            print(self.__trace_position[i])