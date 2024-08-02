from utils.modbus_communication import ModbusCommunication


class TemperatureController:
    def __init__(self, port='COM5', device_ids=[1, 2, 3], json_file='OMEGA_CN616A_Registers_Updated.json'):
        self.comm = ModbusCommunication(port, device_ids=device_ids, json_file=json_file)

    def read_temperature(self, device_id, zone):
        register_name = f'Temperature Zone {zone}'
        return self.comm.read_register(device_id, register_name, 'Temperature Registers Table')

    def set_temperature_setpoint(self, device_id, zone, value):
        register_name = f'Setpoint Zone {zone}'
        self.comm.write_register(device_id, register_name, 'Zone Registers Table', value)

    def enable_all_zones(self, device_id):
        self.comm.enable_all_zones(device_id)
