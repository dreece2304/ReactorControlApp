"""Controller components for ReactorControlApp."""
from .mock_controller import MockTemperatureController

# Try to import real controller, but don't fail if dependencies are missing
try:
    from .controller import TemperatureController
except ImportError:
    TemperatureController = None

__all__ = ['TemperatureController', 'MockTemperatureController']
