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
            2: ["THB", "CB", "DHB", "BTY", "EG", "MPD"],
            3: ["SH1 - C1 and C2", "SH1 - C3 and C4", "SH1 - C5 and C6", "SH2 - C1 and C2", "SH2 - C3 and C4",
                "SH2 - C5 and C6"]
        }

        decimal_points = 0  # Set the desired number of decimal points

        self.controller = TemperatureController(port, device_ids)

        self.zone_tab = ZoneTab(self.controller, device_ids, device_names, zone_names_dict,
                                decimal_points=decimal_points)
        self.setCentralWidget(self.zone_tab)
        self.setWindowTitle("Temperature Controller")
        self.show()
