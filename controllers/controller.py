from utils.modbus_communication import ModbusCommunication

class TemperatureController:
    def __init__(self, port='COM5', device_ids=[1, 2, 3], json_file='C:/Users/bergsman_lab_admin/PycharmProjects/ReactorControlApp/OMEGA_CN616A_Registers.json'):
        self.comm = ModbusCommunication(port, device_ids=device_ids, json_file=json_file)

    def read_temperature(self, device_id, zone):
        base_register = 0x0100 + (zone - 1) * 2  # Calculate the base register for the zone
        return self.comm.read_temperature_registers(device_id, base_register)
