from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .zone_widget import ZoneWidget

class ZoneTab(QWidget):
    def __init__(self, controller, device_ids, device_names, zone_names_dict, decimal_points=2, parent=None):
        super(ZoneTab, self).__init__(parent)
        self.controller = controller
        self.device_ids = device_ids
        self.device_names = device_names
        self.zone_names_dict = zone_names_dict  # Dictionary of zone names for each device
        self.decimal_points = decimal_points

        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        for i, device_id in enumerate(self.device_ids):
            zone_names = self.zone_names_dict.get(device_id, [f"Zone {j + 1}" for j in range(6)])  # Default names if not specified
            zone_widget = ZoneWidget(device_id, self.controller, zone_names, decimal_points=self.decimal_points)
            self.tabs.addTab(zone_widget, self.device_names[i])

        self.setLayout(self.layout)
