from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QHBoxLayout
from PyQt5.QtGui import QFont

class ZoneWidget(QWidget):
    def __init__(self, zone_name, controller, address):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QCheckBox {
                margin-top: 10px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.zone_label = QLabel(zone_name)
        self.zone_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.layout.addWidget(self.zone_label)

        self.show_checkbox = QCheckBox("Show Temperature")
        self.show_checkbox.setChecked(True)
        self.layout.addWidget(self.show_checkbox)

        self.temp_layout = QHBoxLayout()
        self.temp_display = QLineEdit()
        self.temp_display.setReadOnly(True)
        self.temp_layout.addWidget(self.temp_display)

        self.read_button = QPushButton("Read Temperature")
        self.temp_layout.addWidget(self.read_button)

        self.layout.addLayout(self.temp_layout)

        self.setpoint_input = QLineEdit()
        self.setpoint_input.setPlaceholderText("Enter Setpoint")

        self.status_display = QLabel("Status: Valid")

        self.controller = controller
        self.address = address

        self.read_button.clicked.connect(self.update_temperature)
        self.show_checkbox.stateChanged.connect(self.toggle_visibility)

        self.update_temperature_callback = None

        self.layout.addWidget(self.setpoint_input)
        self.layout.addWidget(self.status_display)

    def update_temperature(self):
        temp = self.controller.read_float(self.address)
        status_bitmap = self.controller.read_sensor_status(40396)  # Adjust as needed
        if temp is not None:
            self.temp_display.setText(f"{temp:.2f}")
            if self.update_temperature_callback:
                self.update_temperature_callback()
        else:
            self.temp_display.setText("Error")
        self.update_status(status_bitmap)

    def update_status(self, status_bitmap):
        status = self.interpret_sensor_status(status_bitmap)
        status_text = "Status: " + status
        self.status_display.setText(status_text)

    def interpret_sensor_status(self, status_bitmap):
        status_mapping = {
            0x01: "Valid",
            0x02: "Out of Range Low",
            0x04: "Out of Range High",
            0x08: "Short Circuit",
            0x10: "Open Circuit"
        }
        for bit, text in status_mapping.items():
            if status_bitmap & bit:
                return text
        return "Unknown"

    def toggle_visibility(self):
        widgets = [self.temp_display, self.read_button, self.setpoint_input, self.status_display]
        if self.show_checkbox.isChecked():
            for widget in widgets:
                widget.show()
        else:
            for widget in widgets:
                widget.hide()
