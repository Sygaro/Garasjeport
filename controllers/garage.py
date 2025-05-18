# ==========================================
# Filnavn: garage.py
# Håndtering av portstyring via motorpuls
# ==========================================

from core.system import controller

def handle_port_pulse(port: str, source: str = "api") -> dict:
    """
    Aktiverer motorrelé for gitt port.
    Logger handling og returnerer resultat.
    """
    current_status = controller.get_current_status(port)

    if current_status == "sensor_error":
        return {
            "port": port,
            "success": False,
            "status": current_status,
            "message": "Sensorfeil blokkerer bevegelse"
        }

    relay_result = controller.activate_motor_relay(port, source)
    new_status = controller.get_current_status(port)

    return {
        "port": port,
        "success": relay_result,
        "status": new_status,
        "source": source
    }
