from utils.modbus_communication import ModbusCommunication


class TemperatureController:
    """Interface for reading temperatures from OMEGA CN616A controllers."""

    # Temperature register base address (zone 1 starts at 0x0100)
    TEMP_BASE_REGISTER = 0x0100
    # Each zone occupies 2 consecutive registers
    REGISTERS_PER_ZONE = 2

    def __init__(self, port='COM5', device_ids=None, json_file=None):
        """
        Initialize temperature controller.

        Args:
            port: Serial port (e.g., 'COM5' on Windows, '/dev/ttyUSB0' on Linux)
            device_ids: List of Modbus device IDs (default [1, 2, 3])
            json_file: Path to register configuration JSON (uses default if None)
        """
        if device_ids is None:
            device_ids = [1, 2, 3]
        self.comm = ModbusCommunication(port, device_ids=device_ids, json_file=json_file)

    def read_temperature(self, device_id, zone):
        """
        Read temperature for a specific zone on a device.

        Args:
            device_id: Modbus device address
            zone: Zone number (1-6)

        Returns:
            Temperature in degrees Celsius as float
        """
        # Calculate the base register for the zone
        # Zone 1: 0x0100, Zone 2: 0x0102, Zone 3: 0x0104, etc.
        base_register = self.TEMP_BASE_REGISTER + (zone - 1) * self.REGISTERS_PER_ZONE
        return self.comm.read_temperature_registers(device_id, base_register)

    def close(self):
        """Close serial connections."""
        self.comm.close()
