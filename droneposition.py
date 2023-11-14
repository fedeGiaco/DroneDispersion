from mavsdk import telemetry
from typing import List
from geopy import distance as geo_distance
from geography import deg_to_m, m_to_deg
import math

class DronePosition:
    def __init__(self,
                 latitude_deg:float,
                 longitude_deg:float,
                 absolute_altitude_m:float) -> None:
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.absolute_altitude_m = absolute_altitude_m
    
    #Istanzia la classe a partire da un elemento Position di MAVSDK.
    @classmethod
    def from_mavsdk_position(cls, pos:telemetry.Position) -> None:        
        return cls(pos.latitude_deg, pos.longitude_deg, pos.absolute_altitude_m)

    #Ritorna le nuove coordinate geografiche
    def to_goto_location(self, prev_pos:'DronePosition'=None) -> List[float]:
        if prev_pos == None:
            yaw = 0
        else:
            d_lat = self.latitude_deg - prev_pos.latitude_deg
            d_lon = self.longitude_deg - prev_pos.longitude_deg
            if d_lat > 0:
                tan_angle = 90 + d_lon/d_lat
                yaw = math.atan(tan_angle)
            else:
                yaw = 0
        return (self.latitude_deg, self.longitude_deg, self.absolute_altitude_m, yaw)

    #Calcola le nuove coordinate, sommando le nuove coordinate parametro
    def increment_m(self, lat_increment_m, long_increment_m, alt_increment_m) -> 'DronePosition':
        new_latitude = self.latitude_deg + m_to_deg(lat_increment_m)
        new_longitude = self.longitude_deg + m_to_deg(long_increment_m)
        new_altitude = self.absolute_altitude_m + alt_increment_m
        return DronePosition(new_latitude, new_longitude, new_altitude)