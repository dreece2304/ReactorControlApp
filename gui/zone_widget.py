from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

class ZoneWidget(QWidget):
    def __init__(self, zone_name, controller, address):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.zone_label = QLabel(zone_name)
        self.layout.addWidget(self.zone_label)
        self.temp_display = QLineEdit()
        self.layout.addWidget(self.temp_display)
        self.read_button = QPushButton("Read Temperature")
        self.layout.addWidget(self.read_button)

        self.controller = controller
        self.address = address

        self.read_button.clicked.connect(self.update_temperature)

    def update_temperature(self):
        temp = self.controller.read_float(self.address)
        if temp is not None:
            self.temp_display.setText(f"{temp:.2f}")
        else:
            self.temp_display.setText("Error")
