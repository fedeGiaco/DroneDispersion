from loguru import logger
from mavsdk import System
import random

class SystemWrapper:
    #Crea un elemento System all'indirizzo specificato, lo segnala nel log e lo ritorna in quanto costruttore
    @logger.catch
    def __init__(self,
                 system_addr:int) -> None:
        self.system_addr = system_addr
        self.server_port = random.randint(1000, 65535)
        logger.debug(f"Creating System: system_addr={self.system_addr}, server_port={self.server_port}")
        self.system = System(port=self.server_port)
    
    #Effettua la connessione a un elemento System, lo segnala nel log, quindi lo ritorna già connesso.
    @logger.catch
    async def connect(self) -> System:
        logger.debug(f"Connecting to system@{self.system_addr}")
        await self.system.connect(f"udp://:{self.system_addr}")
        async for state in self.system.core.connection_state():
            if state.is_connected:
                logger.debug("Connection completed")
                break
        logger.debug("Waiting for drone to have a global position estimate...")
        async for health in self.system.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.debug("Global position estimate OK")
                break
        return self.system