import minimalmodbus
import json
import os


class ModbusCommunication:
    def __init__(self, port='COM5', baudrate=115200, device_ids=[1, 2, 3],
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

    def read_registers(self, device_id, register_name, register_type):
        register_info = self.registers.get(register_type)
        if not register_info:
            raise ValueError(f"Register type '{register_type}' not found in the JSON file.")

        registers_to_read = []
        for reg in register_info:
            if reg['Mnemonic'] == register_name:
                registers_to_read.append(int(reg['Index'], 16))

        if len(registers_to_read) != 2:
            raise ValueError(f"Expected 2 registers for {register_name}, but found {len(registers_to_read)}")

        values = [self.devices[device_id].read_register(addr, functioncode=3, signed=False) for addr in
                  registers_to_read]
        combined_value = (values[0] << 16) | values[1]
        return combined_value
