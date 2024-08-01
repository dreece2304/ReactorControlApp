from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class ZoneWidget(QWidget):
    def __init__(self, device_id, controller, parent=None):
        super(ZoneWidget, self).__init__(parent)
        self.device_id = device_id
        self.controller = controller

        self.layout = QVBoxLayout()

        self.name_label = QLabel(self.controller.get_device_name(self.device_id))
        self.temp_label = QLabel("Temperature: N/A")

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.temp_label)

        self.setLayout(self.layout)
        self.update_temperature()

    def update_temperature(self):
        temperature = self.controller.get_temperature(self.device_id)
        self.temp_label.setText(f"Temperature: {temperature if temperature is not None else 'Error'}")
