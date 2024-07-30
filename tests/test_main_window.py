import unittest
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.window = MainWindow()

    def test_window_title(self):
        self.assertEqual(self.window.windowTitle(), "Reactor Temperature Control")

if __name__ == '__main__':
    unittest.main()
