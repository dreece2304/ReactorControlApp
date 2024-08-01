from PyQt5.QtWidgets import QMainWindow
from .zone_tab import ZoneTab
from controllers.controller import TemperatureController

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        port = "COM5"  # The single COM port
        device_ids = [1, 2, 3]  # Add your actual device IDs
        decimal_points = 2  # Set the desired number of decimal points

        self.controller = TemperatureController(port, device_ids)

        self.zone_tab = ZoneTab(self.controller, device_ids, decimal_points=decimal_points)
        self.setCentralWidget(self.zone_tab)
        self.setWindowTitle("Temperature Controller")
        self.show()
