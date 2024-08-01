from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer

class ZoneWidget(QWidget):
    def __init__(self, device_id, controller, decimal_points=2, parent=None):
        super(ZoneWidget, self).__init__(parent)
        self.device_id = device_id
        self.controller = controller
        self.decimal_points = decimal_points

        self.layout = QVBoxLayout()

        self.name_label = QLabel(f"Device {self.device_id}")
        self.layout.addWidget(self.name_label)

        self.zone_labels = []
        for zone in range(6):  # Assuming each device has 6 zones
            zone_label = QLabel(f"Zone {zone + 1}: Temperature: N/A")
            self.layout.addWidget(zone_label)
            self.zone_labels.append(zone_label)

        # Add the "Enable All Zones" button
        self.enable_button = QPushButton("Enable All Zones")
        self.enable_button.clicked.connect(self.enable_all_zones)
        self.layout.addWidget(self.enable_button)

        self.setLayout(self.layout)

        # Set up a timer to update the temperatures every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_temperatures)
        self.timer.start(5000)  # 5000 milliseconds = 5 seconds

    def update_temperatures(self):
        for zone in range(6):
            try:
                temperature = self.controller.read_temperature(self.device_id, zone + 1)  # Zones are 1-indexed
                temperature_formatted = f"{temperature:.{self.decimal_points}f}"  # Format to specified decimal places
            except Exception as e:
                temperature_formatted = f"Error: {e}"
            self.zone_labels[zone].setText(f"Zone {zone + 1}: Temperature: {temperature_formatted}")

    def enable_all_zones(self):
        try:
            self.controller.enable_all_zones(self.device_id)
            print(f"All zones enabled for device {self.device_id}")
        except Exception as e:
            print(f"Error enabling all zones for device {self.device_id}: {e}")
