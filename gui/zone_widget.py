from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QFormLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread, pyqtSignal


class TemperatureReadThread(QThread):
    temperature_read = pyqtSignal(float)
    status_read = pyqtSignal(int)

    def __init__(self, controller, temperature_register, status_register):
        super().__init__()
        self.controller = controller
        self.temperature_register = temperature_register
        self.status_register = status_register

    def run(self):
        temp = self.controller.read_float(self.temperature_register)
        status = self.controller.read_status(self.status_register)
        if temp is not None:
            self.temperature_read.emit(temp)
        if status is not None:
            self.status_read.emit(status)

class ZoneWidget(QWidget):
    def __init__(self, zone_name, controller, temperature_register, status_register):
        super().__init__()
        self.setStyleSheet("""
            QLabel {
                font-size: 12px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 12px;
            }
            QCheckBox {
                margin-top: 10px;
                font-size: 12px;
            }
        """)

        self.layout = QFormLayout(self)
        self.zone_label = QLabel(zone_name)
        self.zone_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.layout.addRow(self.zone_label)

        self.show_checkbox = QCheckBox("Show Temperature")
        self.show_checkbox.setChecked(True)
        self.layout.addRow(self.show_checkbox)

        self.temp_display = QLineEdit()
        self.temp_display.setReadOnly(True)
        self.layout.addRow("Temperature:", self.temp_display)

        self.setpoint_input = QLineEdit()
        self.setpoint_input.setPlaceholderText("Enter Setpoint")
        self.layout.addRow("Setpoint:", self.setpoint_input)

        self.status_display = QLabel("Status: Valid")
        self.layout.addRow("Status:", self.status_display)

        self.controller = controller
        self.temperature_register = temperature_register
        self.status_register = status_register

        print(f"{zone_name}: Temperature Register = {self.temperature_register}, Status Register = {self.status_register}")

        self.show_checkbox.stateChanged.connect(self.toggle_visibility)

        self.update_temperature_callback = None

        self.temperature_thread = None

    def update_temperature(self):
        if self.temperature_thread is not None:
            self.temperature_thread.terminate()

        self.temperature_thread = TemperatureReadThread(self.controller, self.temperature_register, self.status_register)
        self.temperature_thread.temperature_read.connect(self.on_temperature_read)
        self.temperature_thread.status_read.connect(self.on_status_read)
        self.temperature_thread.start()

    def on_temperature_read(self, temp):
        self.temp_display.setText(f"{temp:.2f}")
        if self.update_temperature_callback:
            self.update_temperature_callback()

    def on_status_read(self, status):
        status_text = self.interpret_sensor_status(status)
        self.status_display.setText(f"Status: {status_text}")

    def interpret_sensor_status(self, status):
        status_mapping = {
            0: "Valid",
            1: "Out of Range Low",
            2: "Out of Range High",
            3: "Short Circuit",
            4: "Open Circuit"
        }
        return status_mapping.get(status, "Unknown")

    def toggle_visibility(self):
        widgets = [self.temp_display, self.setpoint_input, self.status_display]
        if self.show_checkbox.isChecked():
            for widget in widgets:
                widget.show()
        else:
            for widget in widgets:
                widget.hide()
