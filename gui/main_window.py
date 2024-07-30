from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from gui.zone_widget import ZoneWidget
from controllers.controller import TemperatureController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reactor Temperature Control")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.controller = TemperatureController('COM3', 1)
        addresses = [40257, 40259, 40261, 40263, 40265, 40267]  # Example addresses for 6 zones

        self.zones = [ZoneWidget(f"Zone {i + 1}", self.controller, addresses[i]) for i in range(6)]
        for zone in self.zones:
            self.layout.addWidget(zone)
