from loguru import logger
from mavsdk import System
import asyncio
from typing import List, Callable
from systemwrapper import SystemWrapper
from droneposition import DronePosition
from geography import distance_2D_m

class Swarm:
    #Gestione dello sciame
    next_drone_address = 14541 
    def __init__(self,
                drones_number:int,
                drones_addrs:List[int]=None) -> None:
        self.__discoveries:List[float] = []
        self.__drones_number = drones_number
        self.__positions = []
        self.__drones:List[System] = []
        self.__every_distance = []
        self.__distance_number = 0
        self.__drones_addrs = []

        #Assegna gli indirizzi corretti a ciascun drone
        if drones_addrs == None:
            for i in range(drones_number):
                self.__drones_addrs.append(Swarm.next_drone_address)
                Swarm.next_drone_address += 1
        elif drones_number != len(drones_addrs):
            raise ValueError; "The number of drones specified does not match with the list size"
        else:
            self.__drones_addrs = drones_addrs
        logger.info(f"Creating swarm with {self.__drones_number} drones at {self.__drones_addrs}")

    #Per ogni drone, tenta la connessione
    async def connect(self):
        logger.info("Connecting to drones...")
        for a in self.__drones_addrs:
            logger.info(f"Connecting to drone@{a}")
            sysW = SystemWrapper(a)
            drone = await sysW.connect()
            logger.info(f"Coonection to drone@{a} completed")
            self.__drones.append(drone)

    #Fai volare tutto lo sciame in contemporanea
    async def takeoff(self):
        logger.info("Taking off")
        for d in self.__drones:
            await d.action.arm()
            await d.action.takeoff()
        logger.info("Takeoff completed")

    #Fai atterrare tutto lo sciame in contemporanea
    async def land(self):
        logger.debug("Landing")
        for d in self.__drones:
            await d.action.land()
        logger.debug("Landing completed")

    #Per ogni drone, calcola e ritorna la posizione in formato DronePosition
    @property
    async def positions(self) -> List[DronePosition]:
        self.__positions = []
        for d in self.__drones:
            p = await d.telemetry.position().__anext__()
            pos = DronePosition.from_mavsdk_position(p)
            self.__positions.append(pos)
        return self.__positions

    #Imposta le nuove posizioni a tutti i droni
    async def set_positions(self, target_positions:List[DronePosition]):
        prev_pos = await self.positions
        for n, d in enumerate(self.__drones):
            pos = target_positions[n]
            await d.action.goto_location(*pos.to_goto_location(prev_pos[n]))

    #Aggiorna il distanza di ogni drone e lo segnala nel log
    async def update_distances(self, begin:List[DronePosition], end:List[DronePosition]):
        for n, d in enumerate(self.__drones):
            pos_begin = begin[n]
            pos_end = end[n]
            offset = distance_2D_m(pos_begin, pos_end)
            self.__every_distance.append(offset)
            logger.info(f"Drone@{self.__drones_addrs[n]} has covered {offset}m")
        self.__distance_number += 1

    #Ritorno l'indirizzo di un solo drone
    async def get_drone_addr_1(self, index_drone: int) -> int:
        return self.__drones_addrs[index_drone]

    #Ritorna l'indirizzo di 2 droni
    def get_drone_addr_2(self, index_drone_0: int, index_drone_1: int) -> [int, int]:
        pos0 = index_drone_0 + 1
        pos1 = index_drone_1 + 1
        drones_selected = [self.__drones_addrs[index_drone_0], self.__drones_addrs[index_drone_1]]
        return drones_selected

    #Ritorno il numero di droni
    @property
    async def get_n_drones(self) -> int:
        return self.__drones_number

    #Ritorno il numero di distanze
    async def get_n_distaces(self, index_drone: int) -> float:
        distance = 0
        lenght = self.__drones_number

        j = index_drone
        for i in range(self.__distance_number):
            distance += self.__every_distance[j]
            j += lenght
        return distance