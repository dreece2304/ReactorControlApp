from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .zone_widget import ZoneWidget


class ZoneTab(QWidget):
    """Tabbed widget containing zone displays for multiple devices."""

    def __init__(self, controller, device_ids, device_names, zone_names_dict,
                 decimal_points=2, update_interval_ms=5000, temperature_history=None,
                 parent=None):
        """
        Initialize zone tabs.

        Args:
            controller: TemperatureController instance
            device_ids: List of device IDs
            device_names: List of device display names
            zone_names_dict: Dict mapping device ID to list of zone names
            decimal_points: Number of decimal places for temperature display
            update_interval_ms: Temperature update interval in milliseconds
            temperature_history: TemperatureHistory instance for logging readings
            parent: Parent widget
        """
        super(ZoneTab, self).__init__(parent)
        self.controller = controller
        self.device_ids = device_ids
        self.device_names = device_names
        self.zone_names_dict = zone_names_dict
        self.decimal_points = decimal_points
        self.update_interval_ms = update_interval_ms
        self.temperature_history = temperature_history

        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.zone_widgets = []
        for i, device_id in enumerate(self.device_ids):
            zone_names = self.zone_names_dict.get(device_id, [f"Zone {j + 1}" for j in range(6)])
            zone_widget = ZoneWidget(device_id, self.controller, zone_names,
                                     decimal_points=self.decimal_points,
                                     update_interval_ms=self.update_interval_ms,
                                     temperature_history=self.temperature_history)
            self.tabs.addTab(zone_widget, self.device_names[i])
            self.zone_widgets.append(zone_widget)

        self.setLayout(self.layout)

    def stop_updates(self):
        """Stop all temperature update timers."""
        for widget in self.zone_widgets:
            widget.stop_updates()

    def set_controller(self, controller):
        """
        Set a new controller for all zone widgets.

        Args:
            controller: New TemperatureController instance
        """
        self.controller = controller
        for widget in self.zone_widgets:
            widget.set_controller(controller)

    def update_zone_names(self, zone_names_dict):
        """
        Update zone names for all devices.

        Args:
            zone_names_dict: Dict mapping device ID to list of zone names
        """
        self.zone_names_dict = zone_names_dict
        for widget in self.zone_widgets:
            device_id = widget.device_id
            if device_id in zone_names_dict:
                widget.update_zone_names(zone_names_dict[device_id])
