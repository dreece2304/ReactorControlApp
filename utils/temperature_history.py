"""Temperature history storage for graphing."""
from collections import deque
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class TemperatureHistory(QObject):
    """
    Centralized storage for temperature history data.

    Stores temperature readings in deques (one per device/zone combination)
    for efficient memory usage with automatic old data removal.
    """

    # Signal emitted when new data is added: (device_id, zone, temperature, timestamp)
    data_added = Signal(int, int, float, object)

    # Maximum number of data points to keep (1 hour at 30-second intervals)
    MAX_POINTS = 120

    def __init__(self, parent=None):
        """Initialize temperature history storage."""
        super().__init__(parent)
        # Structure: {device_id: {zone: deque of (timestamp, temperature)}}
        self._data = {}

    def add_reading(self, device_id, zone, temperature):
        """
        Add a temperature reading to history.

        Args:
            device_id: Device ID number
            zone: Zone number (1-6)
            temperature: Temperature value in Celsius
        """
        timestamp = datetime.now()

        # Ensure device exists in data structure
        if device_id not in self._data:
            self._data[device_id] = {}

        # Ensure zone exists for device
        if zone not in self._data[device_id]:
            self._data[device_id][zone] = deque(maxlen=self.MAX_POINTS)

        # Add the reading
        self._data[device_id][zone].append((timestamp, temperature))

        # Emit signal for listeners
        self.data_added.emit(device_id, zone, temperature, timestamp)

    def get_history(self, device_id, zone):
        """
        Get temperature history for a specific device/zone.

        Args:
            device_id: Device ID number
            zone: Zone number (1-6)

        Returns:
            List of tuples: [(timestamp, temperature), ...]
            Empty list if no data available
        """
        if device_id not in self._data:
            return []
        if zone not in self._data[device_id]:
            return []
        return list(self._data[device_id][zone])

    def get_timestamps(self, device_id, zone):
        """
        Get just the timestamps for a device/zone.

        Args:
            device_id: Device ID number
            zone: Zone number (1-6)

        Returns:
            List of datetime objects
        """
        history = self.get_history(device_id, zone)
        return [t for t, _ in history]

    def get_temperatures(self, device_id, zone):
        """
        Get just the temperature values for a device/zone.

        Args:
            device_id: Device ID number
            zone: Zone number (1-6)

        Returns:
            List of float temperature values
        """
        history = self.get_history(device_id, zone)
        return [temp for _, temp in history]

    def get_device_ids(self):
        """
        Get list of device IDs that have recorded data.

        Returns:
            List of device IDs
        """
        return list(self._data.keys())

    def get_zones_for_device(self, device_id):
        """
        Get list of zones with data for a device.

        Args:
            device_id: Device ID number

        Returns:
            List of zone numbers
        """
        if device_id not in self._data:
            return []
        return list(self._data[device_id].keys())

    def clear(self, device_id=None, zone=None):
        """
        Clear history data.

        Args:
            device_id: If specified, only clear this device
            zone: If specified (with device_id), only clear this zone
        """
        if device_id is None:
            self._data.clear()
        elif zone is None:
            if device_id in self._data:
                self._data[device_id].clear()
        else:
            if device_id in self._data and zone in self._data[device_id]:
                self._data[device_id][zone].clear()

    def get_latest(self, device_id, zone):
        """
        Get the most recent reading for a device/zone.

        Args:
            device_id: Device ID number
            zone: Zone number (1-6)

        Returns:
            Tuple (timestamp, temperature) or None if no data
        """
        history = self.get_history(device_id, zone)
        if history:
            return history[-1]
        return None
