"""Serial port detection utilities."""
import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)


def list_available_ports():
    """
    List all available serial ports on the system.

    Returns:
        List of tuples: (port_name, description, hardware_id)
    """
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append((port.device, port.description, port.hwid))
    return ports


def get_port_names():
    """
    Get just the port names (e.g., COM5, /dev/ttyUSB0).

    Returns:
        List of port name strings
    """
    return [port.device for port in serial.tools.list_ports.comports()]


def is_port_available(port_name):
    """
    Check if a specific port is available.

    Args:
        port_name: Port name to check (e.g., 'COM5')

    Returns:
        bool: True if port exists in available ports
    """
    available = get_port_names()
    return port_name in available


def get_port_description(port_name):
    """
    Get the description for a specific port.

    Args:
        port_name: Port name (e.g., 'COM5')

    Returns:
        str: Port description or None if not found
    """
    for port in serial.tools.list_ports.comports():
        if port.device == port_name:
            return port.description
    return None


def format_port_display(port_name, include_description=True):
    """
    Format a port name for display in the UI.

    Args:
        port_name: Port name (e.g., 'COM5')
        include_description: Whether to include the device description

    Returns:
        str: Formatted display string (e.g., 'COM5 - USB Serial Device')
    """
    if not include_description:
        return port_name

    description = get_port_description(port_name)
    if description and description != port_name:
        return f"{port_name} - {description}"
    return port_name
