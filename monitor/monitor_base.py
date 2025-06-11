# monitor/monitor_base.py
"""
monitor_base.py
Abstrakt baseklasse for alle monitorer i Garasjeport-systemet.
Definerer felles interface og basis-funksjonalitet som alle monitorer skal ha.
"""

import time
from abc import ABC, abstractmethod
from utils.logging.unified_logger import get_logger


class MonitorBase(ABC):
    def __init__(self, config, logger):
        """
        :param config: Konfigurasjonsobjekt eller dict for monitoren
        :param logger: Logger-objekt (fra unified_logger)
        """
        self.logger = get_logger(MonitorBase, category="monitor")
        self.config = config
        self.logger = logger
        self._active = False
        self.last_heartbeat = None

    @abstractmethod
    def start(self):
        """Start overvåkingen (ofte i egen tråd). Skal implementeres av subklassen."""
        pass

    @abstractmethod
    def shutdown(self):
        """Stopper overvåkingen og rydder opp ressurser."""
        pass

    @abstractmethod
    def get_status(self):
        """Returnerer gjeldende status for monitoren (kan være dict eller egendefinert format)."""
        pass

    def heartbeat(self):
        """Oppdaterer sist sett-tidspunkt for monitorens helse."""
        self.last_heartbeat = time.time()
