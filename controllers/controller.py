import minimalmodbus
import serial
import struct

class TemperatureController:
    def __init__(self, port, slave_address, baudrate=115200):
        self.instrument = minimalmodbus.Instrument(port, slave_address)
        self.instrument.serial.baudrate = baudrate
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1

    def read_float(self, address):
        try:
            # Read two 16-bit registers (32-bit value)
            register_address = address - 40001  # Convert Modbus address to zero-based index
            regs = self.instrument.read_registers(register_address, 2, 3)  # Address, number of registers, function code
            if regs:
                # Combine the two 16-bit registers into a 32-bit integer (assuming big-endian format)
                combined = (regs[0] << 16) + regs[1]
                # Convert to IEEE 754 float
                ieee_float = struct.unpack('>f', struct.pack('>I', combined))[0]
                return ieee_float
            else:
                print(f"No response received when reading registers starting at {address}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def read_temperatures(self, addresses):
        temperatures = []
        for address in addresses:
            temp = self.read_float(address)
            temperatures.append(temp)
        return temperatures
