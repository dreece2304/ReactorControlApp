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

    def test_connection(self):
        try:
            # Try reading a common register to test the connection
            self.instrument.read_register(0, 0)
            return True
        except Exception as e:
            print(f"Error testing connection: {e}")
            return False

    def read_float(self, address):
        try:
            register_address = address - 40001  # Convert Modbus address to zero-based index if needed
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
            print(f"Error reading float: {e}")
            return None

# Initialize the controller with the correct port, slave address, and baud rate
port = "COM3"
slave_address = 1
temperature_register = 40257

controller = TemperatureController(port, slave_address)

# Test the connection
if controller.test_connection():
    print("Connection successful.")
else:
    print("Connection failed.")

# Read and print the temperature from Zone 1
temperature = controller.read_float(temperature_register)
if temperature is not None:
    print(f"Temperature from Zone 1: {temperature:.2f} °C")
else:
    print("Failed to read temperature.")
