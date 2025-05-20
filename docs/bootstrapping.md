'''plantuml

@startuml
title initialize_system_environment()

start
:Sjekk/logg mapper;
:Sjekk konfigfiler (JSON);

:Sjekk relay_config:
-> relay_active_state
-> pulse_duration
-> fail_margin_status_change
-> port_status_change_timeout

:Sjekk sensor_config:
-> active_state
-> pull

:Opprett manglende verdier hvis nødvendig;
:Logg resultat;
stop
@enduml
