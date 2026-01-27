"""Configuration loader for ReactorControlApp."""
import configparser
import os
import sys


def get_base_path():
    """Get base path for resources (handles PyInstaller frozen exe)."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Default config file path (relative to project root or exe location)
DEFAULT_CONFIG_FILE = os.path.join(
    get_base_path(),
    'config.ini'
)


class Config:
    """Application configuration loaded from config.ini."""

    def __init__(self, config_file=None):
        """
        Load configuration from file.

        Args:
            config_file: Path to config.ini (uses default if None)
        """
        if config_file is None:
            config_file = DEFAULT_CONFIG_FILE

        self._config_file = config_file

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        self._config = configparser.ConfigParser()
        self._config.read(config_file)

    @property
    def port(self):
        """Serial port for Modbus communication."""
        return self._config.get('serial', 'port', fallback='COM5')

    @property
    def baudrate(self):
        """Serial baudrate."""
        return self._config.getint('serial', 'baudrate', fallback=115200)

    @property
    def device_ids(self):
        """List of Modbus device IDs."""
        ids_str = self._config.get('devices', 'device_ids', fallback='1, 2, 3')
        return [int(x.strip()) for x in ids_str.split(',')]

    @property
    def device_names(self):
        """List of device display names."""
        names_str = self._config.get('devices', 'device_names',
                                     fallback='Device 1, Device 2, Device 3')
        return [x.strip() for x in names_str.split(',')]

    @property
    def decimal_points(self):
        """Number of decimal points for temperature display."""
        return self._config.getint('display', 'decimal_points', fallback=0)

    @property
    def update_interval_ms(self):
        """Update interval in milliseconds."""
        return self._config.getint('display', 'update_interval_ms', fallback=30000)

    def get_zone_names(self, device_id):
        """
        Get zone names for a specific device.

        Args:
            device_id: Device ID number

        Returns:
            List of zone names
        """
        default_names = [f"Zone {i}" for i in range(1, 7)]

        if not self._config.has_option('zone_names', str(device_id)):
            return default_names

        names_str = self._config.get('zone_names', str(device_id))
        names = [x.strip() for x in names_str.split(',')]

        # Ensure we have exactly 6 zone names
        while len(names) < 6:
            names.append(f"Zone {len(names) + 1}")
        return names[:6]

    @property
    def zone_names_dict(self):
        """Dictionary mapping device IDs to zone names."""
        return {device_id: self.get_zone_names(device_id)
                for device_id in self.device_ids}

    def set_port(self, port):
        """
        Set the serial port.

        Args:
            port: Port name (e.g., 'COM5', '/dev/ttyUSB0')
        """
        if not self._config.has_section('serial'):
            self._config.add_section('serial')
        self._config.set('serial', 'port', port)

    def set_zone_names(self, device_id, zone_names):
        """
        Set zone names for a specific device.

        Args:
            device_id: Device ID number
            zone_names: List of 6 zone names
        """
        if not self._config.has_section('zone_names'):
            self._config.add_section('zone_names')

        # Ensure exactly 6 names
        names = list(zone_names)
        while len(names) < 6:
            names.append(f"Zone {len(names) + 1}")
        names = names[:6]

        self._config.set('zone_names', str(device_id), ', '.join(names))

    def save(self):
        """
        Save configuration to file.

        Preserves comments by reading original file and only updating values.
        """
        # Read original file to preserve comments
        original_lines = []
        if os.path.exists(self._config_file):
            with open(self._config_file, 'r') as f:
                original_lines = f.readlines()

        # Build a map of section/key to new values
        updates = {}
        for section in self._config.sections():
            for key, value in self._config.items(section):
                updates[(section.lower(), key.lower())] = value

        # Rewrite file preserving structure and comments
        output_lines = []
        current_section = None
        written_keys = set()

        for line in original_lines:
            stripped = line.strip()

            # Track current section
            if stripped.startswith('[') and stripped.endswith(']'):
                # Before moving to new section, write any unwritten keys for current section
                if current_section:
                    for (sec, key), value in updates.items():
                        if sec == current_section.lower() and (sec, key) not in written_keys:
                            output_lines.append(f"{key} = {value}\n")
                            written_keys.add((sec, key))

                current_section = stripped[1:-1]
                output_lines.append(line)
                continue

            # Check if this is a key=value line
            if current_section and '=' in stripped and not stripped.startswith('#'):
                key_part = stripped.split('=')[0].strip()
                lookup_key = (current_section.lower(), key_part.lower())

                if lookup_key in updates:
                    # Replace with updated value, preserving leading whitespace
                    leading_ws = line[:len(line) - len(line.lstrip())]
                    output_lines.append(f"{leading_ws}{key_part} = {updates[lookup_key]}\n")
                    written_keys.add(lookup_key)
                else:
                    output_lines.append(line)
            else:
                output_lines.append(line)

        # Add any remaining keys for the last section
        if current_section:
            for (sec, key), value in updates.items():
                if sec == current_section.lower() and (sec, key) not in written_keys:
                    output_lines.append(f"{key} = {value}\n")
                    written_keys.add((sec, key))

        # Add any completely new sections
        for section in self._config.sections():
            section_written = any(sec == section.lower() for sec, _ in written_keys)
            if not section_written:
                # Check if any keys from this section need writing
                section_keys = [(sec, key) for (sec, key) in updates.keys() if sec == section.lower()]
                if section_keys:
                    output_lines.append(f"\n[{section}]\n")
                    for sec, key in section_keys:
                        if (sec, key) not in written_keys:
                            output_lines.append(f"{key} = {updates[(sec, key)]}\n")
                            written_keys.add((sec, key))

        # Write updated config
        with open(self._config_file, 'w') as f:
            f.writelines(output_lines)

    def reload(self):
        """Reload configuration from file."""
        self._config = configparser.ConfigParser()
        self._config.read(self._config_file)


def load_config(config_file=None):
    """
    Load configuration from file.

    Args:
        config_file: Path to config.ini (uses default if None)

    Returns:
        Config object
    """
    return Config(config_file)
