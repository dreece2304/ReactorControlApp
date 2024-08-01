from utils.modbus_communication import ModbusCommunication


class TemperatureController:
    def __init__(self, port, device_ids):
        self.comm = ModbusCommunication(port, device_ids=device_ids)
        self.device_names = {device_id: f"Device {device_id}" for device_id in device_ids}

    def get_temperature(self, device_id, zone):
        return self.comm.read_temperature(device_id, zone)

    def set_device_name(self, device_id, name):
        if device_id in self.device_names:
            self.device_names[device_id] = name

    def get_device_name(self, device_id):
        return self.device_names.get(device_id, "Unknown Device")
