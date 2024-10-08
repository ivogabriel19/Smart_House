import time
# Clase base para ESP
class ESP:
    def __init__(self, device_id, device_ip, device_mac, device_type):
        self.ID = device_id
        self.IP = device_ip
        self.MAC = device_mac
        self.status = "Online"
        self.last_seen = time.time()
        self.type = device_type
        self.data = {}
        self.events = []

    def actualizar_last_seen(self):
        self.last_seen = time.time()
    
    def __str__(self):
        return f"{self.ID} {self.IP} {self.MAC} {self.status} {self.type} {self.last_seen} {self.data} "

# Clase Sensor que hereda de ESP
class Sensor(ESP):
    def __init__(self, device_id, device_ip, device_mac):
        super().__init__(device_id, device_ip, device_mac, device_type="Sensor")
        self.data = {"temperatura": "", "humedad": ""}

# Clase Actuador que hereda de ESP
class Actuador(ESP):
    def __init__(self, device_id, device_ip, device_mac):
        super().__init__(device_id, device_ip, device_mac, device_type="Actuador")
        self.data = {"switch": "OFF"}   

class Event:
    def __init__(self, id, alias, type, data, action):
        self.job_id = id,
        self.event_alias = alias,
        self.event_type = type,
        self.event_data = data,
        self.event_action = action
    
    def __str__(self):
        return f"{self.job_id} {self.event_alias} {self.event_type} {self.event_data} {self.event_action} "
