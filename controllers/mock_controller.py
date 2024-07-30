import random
import time

class MockTemperatureController:
    def __init__(self, port, slave_address, baudrate=115200):
        self.port = port
        self.slave_address = slave_address
        self.baudrate = baudrate
        self.zones = [random.uniform(20.0, 25.0) for _ in range(6)]

    def read_float(self, address):
        time.sleep(0.1)  # Simulate some delay
        zone_index = (address - 40257) // 2
        if 0 <= zone_index < len(self.zones):
            return self.zones[zone_index]
        else:
            print(f"Invalid address: {address}")
            return None

    def read_temperatures(self, addresses):
        temperatures = []
        for address in addresses:
            temp = self.read_float(address)
            temperatures.append(temp)
        return temperatures
