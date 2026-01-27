from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer
import logging

logger = logging.getLogger(__name__)


class ZoneWidget(QWidget):
    """Widget displaying temperature readings for all zones on a device."""

    NUM_ZONES = 6  # OMEGA CN616A has 6 zones per device

    def __init__(self, device_id, controller, zone_names, decimal_points=2,
                 update_interval_ms=5000, temperature_history=None, parent=None):
        """
        Initialize zone widget.

        Args:
            device_id: Modbus device address
            controller: TemperatureController instance
            zone_names: List of zone display names
            decimal_points: Number of decimal places for temperature display
            update_interval_ms: Temperature update interval in milliseconds
            temperature_history: TemperatureHistory instance for logging readings
            parent: Parent widget
        """
        super(ZoneWidget, self).__init__(parent)
        self.device_id = device_id
        self.controller = controller
        self.zone_names = list(zone_names)
        self.decimal_points = decimal_points
        self.update_interval_ms = update_interval_ms
        self.temperature_history = temperature_history

        self.layout = QVBoxLayout()

        self.name_label = QLabel(f"Device {self.device_id}")
        self.layout.addWidget(self.name_label)

        self.zone_labels = []
        for zone in range(self.NUM_ZONES):
            zone_label = QLabel(f"{self.zone_names[zone]}: Temperature: N/A")
            self.layout.addWidget(zone_label)
            self.zone_labels.append(zone_label)

        self.setLayout(self.layout)

        # Read the temperatures immediately
        self.update_temperatures()

        # Set up a timer to update the temperatures periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_temperatures)
        self.timer.start(self.update_interval_ms)

    def update_temperatures(self):
        """Read and display current temperatures for all zones."""
        for zone in range(self.NUM_ZONES):
            try:
                temperature = self.controller.read_temperature(self.device_id, zone + 1)
                temperature_formatted = f"{temperature:.{self.decimal_points}f} °C"

                # Log to temperature history if available
                if self.temperature_history is not None:
                    self.temperature_history.add_reading(self.device_id, zone + 1, temperature)

            except KeyError as e:
                temperature_formatted = f"Device not found"
                logger.warning(f"Device {self.device_id} not initialized: {e}")
            except Exception as e:
                temperature_formatted = f"Read error"
                logger.error(f"Error reading device {self.device_id} zone {zone + 1}: {e}")
            self.zone_labels[zone].setText(f"{self.zone_names[zone]}: Temperature: {temperature_formatted}")

    def stop_updates(self):
        """Stop the temperature update timer."""
        self.timer.stop()

    def set_controller(self, controller):
        """
        Set a new controller for temperature readings.

        Args:
            controller: New TemperatureController instance
        """
        self.controller = controller

    def update_zone_names(self, zone_names):
        """
        Update the zone display names.

        Args:
            zone_names: List of 6 zone names
        """
        self.zone_names = list(zone_names)
        # Update labels with new names (temperature will update on next timer tick)
        for zone in range(self.NUM_ZONES):
            current_text = self.zone_labels[zone].text()
            # Extract temperature part if present
            if ": Temperature: " in current_text:
                temp_part = current_text.split(": Temperature: ")[1]
                self.zone_labels[zone].setText(f"{self.zone_names[zone]}: Temperature: {temp_part}")
