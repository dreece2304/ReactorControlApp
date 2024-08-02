from PyQt5.QtWidgets import QMainWindow
from .zone_tab import ZoneTab
from controllers.controller import TemperatureController

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        port = "COM5"  # The single COM port
        device_ids = [1, 2, 3]  # Add your actual device IDs
        device_names = ["Chamber Temperatures", "Local Reactants", "Shared Lines"]  # Custom names for the devices

        # Custom zone names for each device
        zone_names_dict = {
            1: ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"],
            2: ["Zone B1", "Zone B2", "Zone B3", "Zone B4", "Zone B5", "Zone B6"],
            3: ["Zone C1", "Zone C2", "Zone C3", "Zone C4", "Zone C5", "Zone C6"]
        }

        decimal_points = 2  # Set the desired number of decimal points

        self.controller = TemperatureController(port, device_ids)

        self.zone_tab = ZoneTab(self.controller, device_ids, device_names, zone_names_dict,
                                decimal_points=decimal_points)
        self.setCentralWidget(self.zone_tab)
        self.setWindowTitle("Temperature Controller")
        self.show()