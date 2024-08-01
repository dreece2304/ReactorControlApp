from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer


class ZoneWidget(QWidget):
    def __init__(self, device_id, controller, decimal_points=2, parent=None):
        super(ZoneWidget, self).__init__(parent)
        self.device_id = device_id
        self.controller = controller
        self.decimal_points = decimal_points

        self.layout = QVBoxLayout()

        self.name_label = QLabel(self.controller.get_device_name(self.device_id))
        self.layout.addWidget(self.name_label)

        self.zone_labels = []
        for zone in range(6):  # Assuming each device has 6 zones
            zone_label = QLabel(f"Zone {zone}: Temperature: N/A")
            self.layout.addWidget(zone_label)
            self.zone_labels.append(zone_label)

        self.setLayout(self.layout)

        # Set up a timer to update the temperatures every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_temperatures)
        self.timer.start(5000)  # 5000 milliseconds = 5 seconds

    def update_temperatures(self):
        for zone in range(6):
            temperature = self.controller.get_temperature(self.device_id, zone)
            if temperature is not None:
                temperature_formatted = f"{temperature:.{self.decimal_points}f}"  # Format to specified decimal places
            else:
                temperature_formatted = "Error"
            self.zone_labels[zone].setText(f"Zone {zone}: Temperature: {temperature_formatted}")
