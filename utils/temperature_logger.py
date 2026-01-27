"""Temperature data logging to CSV files."""
import csv
import os
import getpass
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Slot
import logging

logger = logging.getLogger(__name__)


class TemperatureLogger(QObject):
    """
    Logs temperature readings to CSV files organized by user/year/month.

    Directory structure:
        base_path/
        └── username/
            └── YYYY/
                └── MM/
                    └── YYYY-MM-DD.csv
    """

    def __init__(self, base_path, device_names=None, zone_names_dict=None, parent=None):
        """
        Initialize temperature logger.

        Args:
            base_path: Base directory for saving CSV files
            device_names: List of device display names
            zone_names_dict: Dict mapping device_id to zone names
            parent: Parent QObject
        """
        super().__init__(parent)
        self.base_path = Path(base_path)
        self.device_names = device_names or {}
        self.zone_names_dict = zone_names_dict or {}
        self.username = getpass.getuser()

        # Set of (device_id, zone) tuples that are being logged
        self._active_zones = set()

        # Track current day's file to know when to rotate
        self._current_date = None
        self._current_file = None
        self._csv_writer = None

        self._is_logging = False

    @property
    def is_logging(self):
        """Whether logging is currently active."""
        return self._is_logging

    def set_device_names(self, device_names):
        """Update device names."""
        self.device_names = device_names

    def set_zone_names(self, zone_names_dict):
        """Update zone names."""
        self.zone_names_dict = zone_names_dict

    def get_active_zones(self):
        """Get set of currently logged zones."""
        return self._active_zones.copy()

    def set_active_zones(self, zones):
        """
        Set which zones to log.

        Args:
            zones: Set of (device_id, zone) tuples
        """
        self._active_zones = set(zones)

    def add_zone(self, device_id, zone):
        """Add a zone to logging."""
        self._active_zones.add((device_id, zone))

    def remove_zone(self, device_id, zone):
        """Remove a zone from logging."""
        self._active_zones.discard((device_id, zone))

    def start_logging(self):
        """Start logging to CSV."""
        if self._is_logging:
            return

        self._is_logging = True
        self._current_date = None  # Force file creation on next write
        logger.info(f"Temperature logging started for {len(self._active_zones)} zones")

    def stop_logging(self):
        """Stop logging and close file."""
        if not self._is_logging:
            return

        self._is_logging = False
        self._close_file()
        logger.info("Temperature logging stopped")

    def _get_file_path(self, date):
        """Get the CSV file path for a given date."""
        # Structure: base_path/username/YYYY/MM/YYYY-MM-DD.csv
        year = date.strftime("%Y")
        month = date.strftime("%m")
        filename = date.strftime("%Y-%m-%d.csv")

        return self.base_path / self.username / year / month / filename

    def _ensure_directory(self, file_path):
        """Ensure the directory for a file exists."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

    def _close_file(self):
        """Close the current CSV file."""
        if self._current_file:
            try:
                self._current_file.close()
            except Exception as e:
                logger.warning(f"Error closing log file: {e}")
            self._current_file = None
            self._csv_writer = None

    def _open_file(self, date):
        """Open or create CSV file for the given date."""
        self._close_file()

        file_path = self._get_file_path(date)
        self._ensure_directory(file_path)

        # Check if file exists to determine if we need headers
        file_exists = file_path.exists()

        try:
            self._current_file = open(file_path, 'a', newline='', encoding='utf-8')
            self._csv_writer = csv.writer(self._current_file)

            # Write header if new file
            if not file_exists:
                self._csv_writer.writerow([
                    'timestamp', 'device_id', 'device_name',
                    'zone', 'zone_name', 'temperature_c'
                ])
                self._current_file.flush()

            self._current_date = date.date()
            logger.info(f"Opened log file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to open log file {file_path}: {e}")
            self._current_file = None
            self._csv_writer = None
            raise

    def _get_device_name(self, device_id):
        """Get display name for a device."""
        if isinstance(self.device_names, list):
            # device_names is a list, device_id is 1-indexed
            idx = device_id - 1
            if 0 <= idx < len(self.device_names):
                return self.device_names[idx]
        elif isinstance(self.device_names, dict):
            return self.device_names.get(device_id, f"Device {device_id}")
        return f"Device {device_id}"

    def _get_zone_name(self, device_id, zone):
        """Get display name for a zone."""
        if device_id in self.zone_names_dict:
            zone_names = self.zone_names_dict[device_id]
            zone_idx = zone - 1
            if 0 <= zone_idx < len(zone_names):
                return zone_names[zone_idx]
        return f"Zone {zone}"

    @Slot(int, int, float, object)
    def log_reading(self, device_id, zone, temperature, timestamp):
        """
        Log a temperature reading if zone is active.

        Args:
            device_id: Device ID number
            zone: Zone number (1-6)
            temperature: Temperature in Celsius
            timestamp: datetime object
        """
        if not self._is_logging:
            return

        if (device_id, zone) not in self._active_zones:
            return

        # Check if we need to rotate to a new day's file
        current_date = timestamp.date() if hasattr(timestamp, 'date') else datetime.now().date()
        if self._current_date != current_date:
            self._open_file(timestamp if hasattr(timestamp, 'date') else datetime.now())

        if self._csv_writer is None:
            return

        try:
            self._csv_writer.writerow([
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                device_id,
                self._get_device_name(device_id),
                zone,
                self._get_zone_name(device_id, zone),
                f"{temperature:.2f}"
            ])
            self._current_file.flush()  # Ensure data is written
        except Exception as e:
            logger.error(f"Failed to write log entry: {e}")

    def get_log_directory(self):
        """Get the current user's log directory."""
        return self.base_path / self.username
