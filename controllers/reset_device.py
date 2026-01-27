"""
Utility script to reset OMEGA CN616A device to factory defaults.

Usage:
    python -m controllers.reset_device [--port PORT] [--device-id ID]
"""
import argparse
import logging
import sys

from utils.modbus_communication import ModbusCommunication

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def reset_device_to_factory_default(port='COM5', device_id=1, json_file=None):
    """
    Reset a device to factory defaults.

    Args:
        port: Serial port (e.g., 'COM5' on Windows, '/dev/ttyUSB0' on Linux)
        device_id: Modbus device address to reset
        json_file: Path to register configuration (uses default if None)
    """
    modbus_comm = None
    try:
        modbus_comm = ModbusCommunication(port=port, device_ids=[device_id], json_file=json_file)
        modbus_comm.write_register(device_id, 'Factory Default', 'System Registers', 1)
        logger.info(f"Device {device_id} on {port} has been reset to factory default.")
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error resetting device {device_id} to factory default: {e}")
        sys.exit(1)
    finally:
        if modbus_comm:
            modbus_comm.close()


def main():
    parser = argparse.ArgumentParser(description='Reset OMEGA CN616A device to factory defaults')
    parser.add_argument('--port', default='COM5',
                        help='Serial port (default: COM5)')
    parser.add_argument('--device-id', type=int, default=1,
                        help='Modbus device ID to reset (default: 1)')
    parser.add_argument('--json-file', default=None,
                        help='Path to register configuration JSON (uses default if not specified)')

    args = parser.parse_args()
    reset_device_to_factory_default(port=args.port, device_id=args.device_id, json_file=args.json_file)


if __name__ == "__main__":
    main()
