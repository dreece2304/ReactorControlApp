from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .zone_widget import ZoneWidget


class ZoneTab(QWidget):
    def __init__(self, controller, device_ids, decimal_points=2, parent=None):
        super(ZoneTab, self).__init__(parent)
        self.controller = controller
        self.device_ids = device_ids
        self.decimal_points = decimal_points

        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        for device_id in self.device_ids:
            zone_widget = ZoneWidget(device_id, self.controller, decimal_points=self.decimal_points)
            self.tabs.addTab(zone_widget, self.controller.get_device_name(device_id))

        self.setLayout(self.layout)
