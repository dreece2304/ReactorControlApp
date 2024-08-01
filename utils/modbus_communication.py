import minimalmodbus
import json
import os


class ModbusCommunication:
    def __init__(self, port, baudrate=115200, device_ids=[1, 2, 3], json_file='OMEGA_CN616A_Registers.json'):
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

    def read_register(self, device_id, register_name, register_type):
        register_info = self.registers.get(register_type)
        if not register_info:
            raise ValueError(f"Register type '{register_type}' not found in the JSON file.")

        for reg in register_info:
            if reg['Mnemonic'] == register_name:
                register_address = int(reg['Index'], 16)
                value = self.devices[device_id].read_register(register_address, functioncode=3, signed=False)
                return value
        raise ValueError(f"Register '{register_name}' not found in '{register_type}'.")

    def write_register(self, device_id, register_name, register_type, value):
        register_info = self.registers.get(register_type)
        if not register_info:
            raise ValueError(f"Register type '{register_type}' not found in the JSON file.")

        for reg in register_info:
            if reg['Mnemonic'] == register_name:
                register_address = int(reg['Index'], 16)
                self.devices[device_id].write_register(register_address, value, functioncode=16)
                return
        raise ValueError(f"Register '{register_name}' not found in '{register_type}'.")

    def enable_all_zones(self, device_id):
        for zone in range(1, 7):  # Assuming there are 6 zones
            register_name = f'Zone {zone} Enable'
            try:
                self.write_register(device_id, register_name, 'Zone Registers Table',
                                    1)  # Assuming 1 is the enable value
            except ValueError as e:
                print(f"Error enabling zone {zone} for device {device_id}: {e}")
