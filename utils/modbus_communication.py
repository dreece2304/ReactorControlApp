import minimalmodbus
import json
import os
import struct


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

    def read_temperature_registers(self, device_id, base_register):
        # Read two consecutive 16-bit registers and combine them into a 32-bit IEEE float
        msb_value = self.devices[device_id].read_register(base_register, functioncode=3, signed=False)
        lsb_value = self.devices[device_id].read_register(base_register + 1, functioncode=3, signed=False)
        combined_value = (msb_value << 16) | lsb_value

        # Interpret the combined value as a 32-bit IEEE floating-point number
        float_value = struct.unpack('>f', combined_value.to_bytes(4, byteorder='big'))[0]
        return float_value

    def write_register(self, device_id, register_name, register_type, value):
        register_info = self.registers.get(register_type)
        if not register_info:
            raise ValueError(f"Register type '{register_type}' not found in the JSON file.")

        for reg in register_info:
            if reg['Mnemonic'] == register_name:
                register_address = int(reg['Index'], 16) + 1  # Adjust index for Modbus
                self.devices[device_id].write_register(register_address, value,
                                                       functioncode=6)  # Use function code 6 for writing a single register
                return
        raise ValueError(f"Register '{register_name}' not found in '{register_type}'.")

