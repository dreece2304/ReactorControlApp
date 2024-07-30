import unittest
from PyQt5.QtWidgets import QApplication
from gui.zone_widget import ZoneWidget
from controllers.controller import TemperatureController

class TestZoneWidget(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.controller = TemperatureController('COM3', 1)
        self.widget = ZoneWidget("Zone 1", self.controller, 40257)

    def test_update_temperature(self):
        self.widget.update_temperature()
        temp_display_text = self.widget.temp_display.text()
        self.assertTrue(temp_display_text)

if __name__ == '__main__':
    unittest.main()
