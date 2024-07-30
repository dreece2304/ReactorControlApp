import unittest
from controllers.controller import TemperatureController

class TestTemperatureController(unittest.TestCase):
    def test_read_float(self):
        controller = TemperatureController('COM3', 1)
        # Assuming the test environment is set up to return a specific value
        temp = controller.read_float(40257)
        self.assertIsNotNone(temp)
        self.assertIsInstance(temp, float)

if __name__ == '__main__':
    unittest.main()
