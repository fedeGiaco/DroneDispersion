from swarm import Swarm
import asyncio
import random
from droneposition import DronePosition
from trace import Trace
from loguru import logger
import math
from math import floor
from geography import deg_to_m, m_to_deg, distance_2D_xy, distance_2D_m

#Converti le coordinate geografiche in cartesiane
def get_cartesian_coordinates(lower_bound_x: float,
                lower_bound_y: float,
                side_length: float,
                total_points: int,
                position: DronePosition) -> (int, int):

    pos_x = position.latitude_deg
    pos_y = position.longitude_deg
    pos_x_m = deg_to_m(pos_x)
    pos_y_m = deg_to_m(pos_y)
    point_length = math.ceil(side_length/total_points)

    x_index = math.floor((pos_x_m - lower_bound_x) / point_length)
    y_index = math.floor((pos_y_m - lower_bound_y) / point_length)
    return (x_index, y_index)

#Calcola i confini della mappa
def calculate_boundaries(drone_position_x: float, drone_position_y: float, side_length: float) -> list[tuple]:

    half_side = side_length / 2.0
    drone_position_x = floor(drone_position_x)
    drone_position_y = floor(drone_position_y)

    upper_left = (drone_position_x - half_side, drone_position_y + half_side)
    upper_right = (drone_position_x + half_side, drone_position_y + half_side)
    lower_left = (drone_position_x - half_side, drone_position_y - half_side)
    lower_right = (drone_position_x + half_side, drone_position_y - half_side)
    return [upper_left, upper_right, lower_left, lower_right]

#Calcola la prossima posizione casuale, ritorna una posizione alla volta
async def next_random_location(swarm:Swarm, max_distance: int, drone_n: int) -> DronePosition:

    #Recupera le posizioni iniziali e seleziona quella del drone passato come parametro
    starting_pos = await swarm.positions
    begin = starting_pos[drone_n]

    #Genera nuove coordinate geografiche casuali
    alpha = 2 * math.pi * random.random()
    u = random.random() + random.random()
    r = max_distance * (2 - u if u > 1 else u)
    new_latitude = r * math.cos(alpha)
    new_longitude = r * math.sin(alpha)
    good_distance = math.ceil(max_distance/5)
    new_altitude = random.randrange(0, good_distance)

    go_to_position = begin.increment_m(new_latitude, new_longitude, new_altitude)
    return go_to_position

#Ritorna chi ha colliso O se non ci sono collisioni con le tracce
async def trace_routine(trace:Trace, swarm:Swarm, spawn:list[DronePosition]) -> list:
    
    #Recupero i confini della mappa, basandomi sul primo drone, quindi il numero di droni
    boundaries = calculate_boundaries(deg_to_m(spawn[0].latitude_deg), deg_to_m(spawn[0].longitude_deg), 100)
    n_drones = await swarm.get_n_drones
    range_trace = 0
    trace_count = 0
    avoid_count = 0
    last_index = -1
    drones_exit = []
    trace_count_max = trace.get_trace_check()

    while True:
        #Recupero la posizione corrente dei droni
        drone_positions = await swarm.positions
        #Calcolo ciascuna posizione (x,y,z) per ogni drone
        corrent_positions_axis = [get_cartesian_coordinates(boundaries[0][0], boundaries[2][1], 100, 20, d) for d in drone_positions]
        await trace.add_position(corrent_positions_axis)
        trace_count += 1

        #Dopo ALMENO 3 spostamenti di ciascun drone, controlla la traccia
        if trace_count >= 3:
            for j in range(n_drones):
                last_index = -1
                position_compare = trace.get_position(0, j)
                if trace_count < trace_count_max:
                    range_trace = trace_count
                else:
                    range_trace = trace_count_max
                for i in range(range_trace):
                    for k in range(n_drones):
                        if k != j:
                            #Se la posizione di un qualsiasi drone si avvicina troppo con una qualsiasi traccia recente (sua esclusa), ritorna l'indice dello stesso
                            position_danger = trace.get_position(i, k)
                            distance = distance_2D_xy(position_compare, position_danger)
                            #print(f"i:{i}, j:{j}, k:{k}, compare:{position_compare}, danger:{position_danger}, distance:{distance}")
                            if distance < 2.0:
                                avoid_count += 1
                                avoid_element = [j, k, distance]
                                #print(f"COLLISION - i:{i}, j:{j}, k:{k}, avoid_element:{avoid_count}")
                                drones_exit.append(avoid_element) 
                                last_index = j
                        if j == last_index:
                            break
                    if j == last_index:
                        break
        
        #C'è stata almeno una collisione
        if avoid_count > 0:
            return drones_exit

        if trace_count >= 2:
            pos0 = trace.get_every_position(0)
            pos1 = trace.get_every_position(1)
            if pos0 == pos1:
                stop_element = [-1, -1, -1]
                drones_exit.append(stop_element)
                return drones_exit

        #Attenti 1s prima di ripartire altrimenti la coordinate rimangono invariate a causa dell'approssimazione
        await asyncio.sleep(1)

async def print_sum_distance(swarm: Swarm):
    distance = 0
    total_distance = 0
    n_drones = await swarm.get_n_drones

    for i in range(n_drones):
        distance = await swarm.get_n_distaces(i)
        address = await swarm.get_drone_addr_1(i)
        total_distance += distance
        logger.info(f"Distance covered by @drone{address}: {distance}m")
        distance = 0
    logger.info(f"Total distance: {total_distance}m")

async def main():

    drone_quantity = 3

    #Inizializzazione dello sciame
    sw = Swarm(drone_quantity)
    n_change = 0

    #Avvio
    await sw.connect()
    await sw.takeoff()
    await asyncio.sleep(5)
    all_trace = Trace(drone_quantity, drone_quantity)
    
    #Recupera le posizioni iniziali, quindi genera direzioni casuali e impostale per tutti i droni
    position_start = await sw.positions
    position_end = []
    for n, p in enumerate(position_start):
        next_position = await next_random_location(sw, 20, n)  #da soli si spostano fino a 20m
        n += 1
        position_end.append(next_position)
    await sw.set_positions(position_end)

    #Dispersione fino a 15 iterazioni
    while n_change < 15:

        position_future = []
        position_end = await sw.positions

        #Monitora i tracciati e gestisci i droni interessati da una distanza troppo ravvicinata o che si sono fermati
        drones_result = await trace_routine(all_trace, sw, position_end)
        position_new = await sw.positions

        await sw.update_distances(position_end, position_new)

        drones_what = drones_result[0]
        drones_if = drones_what[0]
        drones_count = len(drones_result)
        position_future = await sw.positions
        n_change += 1
        logger.debug(f"Number of changes: {n_change}")

        if(drones_if >= 0):
            #Aggiorna la posizione SOLO ai droni interessati
            for i in range(drones_count):
                drone_choose = drones_result[i]
                drone_info_who = drone_choose[0]
                drone_info_where = drone_choose[1]
                drone_info_distance = drone_choose[2]
                drone_addr = sw.get_drone_addr_2(drone_info_who, drone_info_where)

                logger.info(f"Drone@{drone_addr[0]} was at {drone_info_distance}m from the trace of Drone@{drone_addr[1]}")                
                next_position = await next_random_location(sw, 50, drone_info_who)
                position_future[drone_info_who] = next_position
            await sw.set_positions(position_future)

        else:
            #Aggiorna la posizione a tutti poichè sono fermi
            logger.info(f"Every drone has done an indipendent route and has stopped, so everyone restart")
            position_start = await sw.positions
            position_end = []
            for n, p in enumerate(position_start):
                next_position = await next_random_location(sw, 20, n)
                n += 1
                position_end.append(next_position)
            await sw.set_positions(position_end)

    #Stampa la distanza percorsa
    await print_sum_distance(sw)
    #Quindi atterra
    await sw.land()
    
if __name__ == "__main__":
    asyncio.run(main())