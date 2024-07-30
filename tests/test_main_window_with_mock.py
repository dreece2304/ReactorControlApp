import unittest
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.zone_widget import ZoneWidget  # Import ZoneWidget
from controllers.mock_controller import MockTemperatureController
import sys


class TestMainWindowWithMock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.controller = MockTemperatureController('COM3', 1)
        self.window = MainWindow()

        # Replace the real controller with the mock controller
        self.window.controller = self.controller

        addresses = [40257, 40259, 40261, 40263, 40265, 40267]  # Example addresses for 6 zones
        self.window.zones = [
            ZoneWidget(f"Zone {i + 1}", self.window.controller, addresses[i]) for i in range(6)
        ]
        for zone in self.window.zones:
            self.window.layout.addWidget(zone)

    def test_window_title(self):
        self.assertEqual(self.window.windowTitle(), "Reactor Temperature Control")

    def test_zone_widgets(self):
        for zone_widget in self.window.zones:
            self.assertIsNotNone(zone_widget)

    def test_read_temperatures(self):
        for zone_widget in self.window.zones:
            zone_widget.update_temperature()
            temp_display_text = zone_widget.temp_display.text()
            self.assertTrue(temp_display_text)


if __name__ == '__main__':
    unittest.main()
