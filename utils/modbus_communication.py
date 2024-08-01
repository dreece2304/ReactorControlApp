import minimalmodbus
import struct


class ModbusCommunication:
    def __init__(self, port, baudrate=115200, device_ids=[1, 2, 3]):
        self.devices = {}
        for device_id in device_ids:
            instrument = minimalmodbus.Instrument(port, device_id)
            instrument.serial.baudrate = baudrate
            instrument.serial.timeout = 1
            instrument.mode = minimalmodbus.MODE_RTU
            self.devices[device_id] = instrument

    def read_temperature(self, device_id, zone):
        register_start = 0x0100 + zone * 2  # Starting address for the zones
        try:
            # Read two registers (4 bytes) for the IEEE 754 floating point number
            registers = self.devices[device_id].read_registers(register_start, 2, functioncode=3)
            # Convert the registers to a float
            ieee_float = struct.unpack('>f', struct.pack('>HH', registers[0], registers[1]))[0]
            return ieee_float
        except Exception as e:
            print(f"Error reading temperature from device {device_id} zone {zone}: {e}")
            return None
