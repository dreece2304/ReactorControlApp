from PyQt5.QtWidgets import QMainWindow, QApplication
from .zone_tab import ZoneTab
from controllers.controller import TemperatureController


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        ports = ["COM3", "COM4", "COM5"]  # Replace with your actual ports
        device_ids = [1, 2, 3]  # Add your actual device IDs

        self.controller = TemperatureController(ports, device_ids)

        self.zone_tab = ZoneTab(self.controller, device_ids)
        self.setCentralWidget(self.zone_tab)
        self.setWindowTitle("Temperature Controller")
        self.show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()
