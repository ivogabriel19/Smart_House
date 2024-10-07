import time

class ESP:
    def __init__(self, id, ip, mac, status, type, data):
        self.ID = id,
        self.IP = ip,
        self.MAC = mac,
        self.status = status,
        self.type = type,
        self.last_seen = time.time(),
        self.data = {}
    
    def __str__(self):
        return f"{self.ID} {self.IP} {self.MAC} {self.status} {self.type} {self.last_seen} {self.data} "

class Event:
    def __init__(self, id, alias, type, data, action):
        self.job_id = id,
        self.event_alias = alias,
        self.event_type = type,
        self.event_data = data,
        self.event_action = action
    
    def __str__(self):
        return f"{self.job_id} {self.event_alias} {self.event_type} {self.event_data} {self.event_action} "
