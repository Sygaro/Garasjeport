# controllers/port_controller.py

from core.garage_controller import GarageController

class PortController:
    def __init__(self):
        self.controller = GarageController()

    def get_status(self, port):
        """Returnerer status: 'open', 'closed', 'moving', 'partial', 'error'"""
        return self.controller.get_status(port)

    def is_open(self, port):
        return self.get_status(port) == "open"

    def toggle_port(self, port):
        """Sender puls til port hvis mulig"""
        return self.controller.trigger_pulse(port)
