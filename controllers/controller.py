from utils.modbus_communication import ModbusCommunication

class TemperatureController:
    def __init__(self, port='COM5', device_ids=[1, 2, 3], json_file='C:/Users/bergsman_lab_admin/PycharmProjects/ReactorControlApp/OMEGA_CN616A_Registers.json'):
        self.comm = ModbusCommunication(port, device_ids=device_ids, json_file=json_file)

    def read_temperature(self, device_id, zone):
        register_names = [f'Temperature Zone {2 * zone - 1}', f'Temperature Zone {2 * zone}']
        temperature = 0
        for register_name in register_names:
            temperature = (temperature << 16) | self.comm.read_register(device_id, register_name, 'Temperature Registers')
        return temperature
