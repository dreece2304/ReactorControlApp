from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QTabWidget, QLineEdit, QPushButton, QHBoxLayout, QCheckBox, QSizePolicy, QGroupBox, QSpacerItem
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

# Set to True if using Mock controller for testing
USE_MOCK_CONTROLLER = True

if USE_MOCK_CONTROLLER:
    from controllers.mock_controller import MockTemperatureController as TemperatureController
else:
    from controllers.controller import TemperatureController

from gui.zone_widget import ZoneWidget
from gui.zone_tab import ZoneTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reactor Temperature Control")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.header = QLabel("Reactor Temperature Control")
        self.header.setFont(QFont("Arial", 18, QFont.Bold))
        self.layout.addWidget(self.header)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.main_tab = QWidget()
        self.tab_widget.addTab(self.main_tab, "Main")
        self.main_layout = QVBoxLayout(self.main_tab)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.interval_group = QGroupBox("Update Interval")
        self.interval_layout = QHBoxLayout()
        self.interval_label = QLabel("Update Interval (ms):")
        self.interval_input = QLineEdit("5000")
        self.set_interval_button = QPushButton("Set Interval")
        self.set_interval_button.clicked.connect(self.set_update_interval)

        self.interval_layout.addWidget(self.interval_label)
        self.interval_layout.addWidget(self.interval_input)
        self.interval_layout.addWidget(self.set_interval_button)
        self.interval_group.setLayout(self.interval_layout)
        self.main_layout.addWidget(self.interval_group)

        self.controller = TemperatureController('COM3', 1)
        addresses = [40257, 40259, 40261, 40263, 40265, 40267]  # Example addresses for 6 zones

        self.zones = [ZoneWidget(f"Zone {i+1}", self.controller, addresses[i]) for i in range(6)]

        self.zones_group = QGroupBox("Zones Status")
        self.zones_layout = QGridLayout()
        for i, zone in enumerate(self.zones):
            label = QLabel(f"Zone {i+1}")
            setpoint_label = QLabel("Setpoint (°C):")
            status_label = QLabel("Status:")
            self.zones_layout.addWidget(label, i, 0)
            self.zones_layout.addWidget(zone.show_checkbox, i, 1)
            self.zones_layout.addWidget(zone.temp_display, i, 2)
            self.zones_layout.addWidget(setpoint_label, i, 3)
            self.zones_layout.addWidget(zone.setpoint_input, i, 4)
            self.zones_layout.addWidget(status_label, i, 5)
            self.zones_layout.addWidget(zone.status_display, i, 6)
        self.zones_group.setLayout(self.zones_layout)
        self.main_layout.addWidget(self.zones_group)

        for i, zone in enumerate(self.zones):
            zone_tab = ZoneTab(zone)
            self.tab_widget.addTab(zone_tab, f"Zone {i+1}")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all_temperatures)
        self.timer.start(5000)  # Default update every 5 seconds

    def set_update_interval(self):
        interval = int(self.interval_input.text())
        self.timer.setInterval(interval)

    def update_all_temperatures(self):
        for zone in self.zones:
            if zone.show_checkbox.isChecked():
                zone.update_temperature()
