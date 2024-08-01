import minimalmodbus


class ModbusCommunication:
    def __init__(self, ports, baudrate=115200, device_ids=[1, 2, 3]):
        self.devices = {}
        for port, device_id in zip(ports, device_ids):
            instrument = minimalmodbus.Instrument(port, device_id)
            instrument.serial.baudrate = baudrate
            instrument.serial.timeout = 1
            instrument.mode = minimalmodbus.MODE_RTU
            self.devices[device_id] = instrument

    def read_temperature(self, device_id, register):
        try:
            return self.devices[device_id].read_register(register, 1)
        except Exception as e:
            print(f"Error reading temperature from device {device_id}: {e}")
            return None
