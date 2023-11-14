from geopy import distance as geo_distance
import math

#Converte da gradi a metri
def deg_to_m(deg) -> float:
    # 1 deg = 111319.9 m
    return deg * 111319.9

#Converte da metri a gradi
def m_to_deg(m) -> float:
    return m / 111319.9

#Calcola la distanza fra 2 punti in coordinate polari
def distance_2D_xy(partenza:[int, int], arrivo:[int, int]) -> float:
    point_x = arrivo[1] - partenza[1]
    point_y = arrivo[0] - partenza[0]
    distance = math.sqrt(math.pow(point_x,2) + math.pow(point_y,2))
    return distance

#Calcola la distanza fra 2 punti in coordinate geografiche
def distance_2D_m(partenza:'DronePosition', arrivo:'DronePosition') -> float:
    point1 = (partenza.latitude_deg, partenza.longitude_deg)
    point2 = (arrivo.latitude_deg, arrivo.longitude_deg)
    distance = geo_distance.distance(point1, point2).meters
    return distance