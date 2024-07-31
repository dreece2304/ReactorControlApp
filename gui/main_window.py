from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QLineEdit, QPushButton, QGroupBox, \
    QHBoxLayout, QFormLayout
from PyQt5.QtCore import QTimer
from .zone_widget import ZoneWidget
from .zone_tab import ZoneTab
from controllers.controller import TemperatureController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reactor Temperature Control")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.header = QLabel("Reactor Temperature Control")
        self.layout.addWidget(self.header)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.main_tab = QWidget()
        self.tab_widget.addTab(self.main_tab, "Main")
        self.main_layout = QVBoxLayout(self.main_tab)

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

        self.device_id_label = QLabel("Device ID: N/A")
        self.main_layout.addWidget(self.device_id_label)

        self.zones_group = QGroupBox("Zones Status")
        self.zones_form_layout = QFormLayout()
        self.zones_group.setLayout(self.zones_form_layout)
        self.main_layout.addWidget(self.zones_group)

        self.controller_port = "COM3"
        self.slave_address = 1
        self.baudrate = 115200
        self.zones_per_controller = 6

        # Initialize controller
        self.controller = TemperatureController(self.controller_port, self.slave_address, self.baudrate)

        # Read and display the device ID
        self.display_device_id()

        # Add zones with correct register addresses
        self.zones = []
        for i in range(self.zones_per_controller):
            temperature_register = 40257 + i
            status_register = 40385 + i
            zone = ZoneWidget(f"Zone {i + 1}", self.controller, temperature_register, status_register)
            self.zones.append(zone)
            self.zones_form_layout.addRow(zone.zone_label, zone)

        # Add a single "Read Temperature" button for all zones
        self.read_all_button = QPushButton("Read All Temperatures")
        self.read_all_button.clicked.connect(self.update_all_temperatures)
        self.main_layout.addWidget(self.read_all_button)

        # Add zone tabs with graphs
        for zone in self.zones:
            zone_tab = ZoneTab(zone)
            self.tab_widget.addTab(zone_tab, zone.zone_label.text())

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

    def display_device_id(self):
        device_id = self.controller.read_device_id()
        if device_id is not None:
            self.device_id_label.setText(f"Device ID: {device_id}")
        else:
            self.device_id_label.setText("Device ID: Error")
