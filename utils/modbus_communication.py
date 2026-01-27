import minimalmodbus
import json
import os
import struct
import logging

logger = logging.getLogger(__name__)

# Default path to register configuration file (relative to this module)
DEFAULT_REGISTER_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'OMEGA_CN616A_Registers.json'
)


class ModbusCommunication:
    def __init__(self, port='COM5', baudrate=115200, device_ids=None, json_file=None):
        """
        Initialize Modbus communication with temperature controllers.

        Args:
            port: Serial port (e.g., 'COM5' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Communication speed (default 115200)
            device_ids: List of Modbus device IDs (default [1, 2, 3])
            json_file: Path to register configuration JSON (default: OMEGA_CN616A_Registers.json)
        """
        if device_ids is None:
            device_ids = [1, 2, 3]
        if json_file is None:
            json_file = DEFAULT_REGISTER_FILE

        self.devices = {}
        self.load_registers(json_file)

        for device_id in device_ids:
            try:
                instrument = minimalmodbus.Instrument(port, device_id)
                instrument.serial.baudrate = baudrate
                instrument.serial.timeout = 1
                self.devices[device_id] = instrument
                logger.debug(f"Initialized device {device_id} on {port}")
            except Exception as e:
                logger.error(f"Failed to initialize device {device_id} on {port}: {e}")
                raise

    def load_registers(self, json_file):
        """Load register configuration from JSON file."""
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"JSON file '{json_file}' not found.")
        with open(json_file, 'r') as file:
            self.registers = json.load(file)
        logger.debug(f"Loaded registers: {list(self.registers.keys())}")

    def read_temperature_registers(self, device_id, base_register):
        """
        Read temperature from two consecutive 16-bit registers as IEEE 754 float.

        Args:
            device_id: Modbus device address
            base_register: Starting register address (0x0100 for zone 1, etc.)

        Returns:
            Temperature as float

        Raises:
            KeyError: If device_id not initialized
            minimalmodbus.ModbusException: On communication error
        """
        if device_id not in self.devices:
            raise KeyError(f"Device {device_id} not initialized")

        try:
            # Read two consecutive 16-bit registers and combine them into a 32-bit IEEE float
            msb_value = self.devices[device_id].read_register(base_register, functioncode=3, signed=False)
            lsb_value = self.devices[device_id].read_register(base_register + 1, functioncode=3, signed=False)
            combined_value = (msb_value << 16) | lsb_value

            # Interpret the combined value as a 32-bit IEEE floating-point number
            float_value = struct.unpack('>f', combined_value.to_bytes(4, byteorder='big'))[0]
            return float_value
        except minimalmodbus.ModbusException as e:
            logger.error(f"Modbus error reading device {device_id} register {hex(base_register)}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading temperature from device {device_id}: {e}")
            raise

    def write_register(self, device_id, register_name, register_type, value):
        """
        Write a value to a named register.

        Args:
            device_id: Modbus device address
            register_name: Register mnemonic (e.g., 'Factory Default')
            register_type: Register category (e.g., 'System Registers')
            value: Value to write

        Raises:
            ValueError: If register type or name not found
            KeyError: If device_id not initialized
        """
        if device_id not in self.devices:
            raise KeyError(f"Device {device_id} not initialized")

        register_info = self.registers.get(register_type)
        if not register_info:
            raise ValueError(f"Register type '{register_type}' not found in the JSON file.")

        for reg in register_info:
            if reg['Mnemonic'] == register_name:
                register_address = int(reg['Index'], 16) + 1  # Adjust index for Modbus
                self.devices[device_id].write_register(register_address, value, functioncode=6)
                logger.debug(f"Wrote value {value} to register {register_name} on device {device_id}")
                return
        raise ValueError(f"Register '{register_name}' not found in '{register_type}'.")

    def close(self):
        """Close all serial connections."""
        for device_id, instrument in self.devices.items():
            try:
                instrument.serial.close()
                logger.debug(f"Closed connection to device {device_id}")
            except Exception as e:
                logger.warning(f"Error closing device {device_id}: {e}")

