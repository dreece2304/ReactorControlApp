import minimalmodbus
import json
import os


class ModbusCommunication:
    def __init__(self, port='COM5', baudrate=115200, device_ids=[1],
                 json_file='C:/Users/bergsman_lab_admin/PycharmProjects/ReactorControlApp/OMEGA_CN616A_Registers.json'):
        self.devices = {}
        self.load_registers(json_file)
        for device_id in device_ids:
            instrument = minimalmodbus.Instrument(port, device_id)
            instrument.serial.baudrate = baudrate
            instrument.serial.timeout = 1
            self.devices[device_id] = instrument

    def load_registers(self, json_file):
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"JSON file '{json_file}' not found.")
        with open(json_file, 'r') as file:
            self.registers = json.load(file)
        print(f"Loaded registers: {self.registers.keys()}")  # Debugging output

    def write_register(self, device_id, register_name, register_type, value):
        register_info = self.registers.get(register_type)
        if not register_info:
            raise ValueError(f"Register type '{register_type}' not found in the JSON file.")

        for reg in register_info:
            if reg['Mnemonic'] == register_name:
                register_address = int(reg['Index'], 16)  # Adjust index for Modbus
                self.devices[device_id].write_register(register_address, value,
                                                       functioncode=6)  # Use function code 6 for writing a single register
                return
        raise ValueError(f"Register '{register_name}' not found in '{register_type}'.")


def reset_device_to_factory_default():
    port = 'COM5'
    device_id = 1
    json_file = 'C:/Users/bergsman_lab_admin/PycharmProjects/ReactorControlApp/OMEGA_CN616A_Registers.json'
    modbus_comm = ModbusCommunication(port=port, device_ids=[device_id], json_file=json_file)

    # Reset the device to factory default
    try:
        modbus_comm.write_register(device_id, 'Factory Default', 'System Registers', 1)  # Assuming 1 triggers the reset
        print(f"Device {device_id} has been reset to factory default.")
    except Exception as e:
        print(f"Error resetting device {device_id} to factory default: {e}")


if __name__ == "__main__":
    reset_device_to_factory_default()
