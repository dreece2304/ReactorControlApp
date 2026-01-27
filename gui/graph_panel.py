"""Dockable panel containing the temperature graph."""
from PySide6.QtWidgets import QDockWidget
from PySide6.QtCore import Qt
from .graph_widget import TemperatureGraphWidget


class GraphPanel(QDockWidget):
    """Dockable panel for the temperature graph."""

    def __init__(self, temperature_history, device_ids, device_names, zone_names_dict,
                 parent=None):
        """
        Initialize the graph panel.

        Args:
            temperature_history: TemperatureHistory instance
            device_ids: List of device IDs
            device_names: List of device display names
            zone_names_dict: Dict mapping device ID to zone names
            parent: Parent widget
        """
        super().__init__("Temperature Graph", parent)

        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea |
                            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable |
                        QDockWidget.DockWidgetMovable |
                        QDockWidget.DockWidgetFloatable)

        # Create and set the graph widget
        self.graph_widget = TemperatureGraphWidget(
            temperature_history,
            device_ids,
            device_names,
            zone_names_dict
        )
        self.setWidget(self.graph_widget)

        # Set minimum size for the dock
        self.setMinimumHeight(250)

    def update_zone_names(self, zone_names_dict):
        """
        Update zone names in the graph widget.

        Args:
            zone_names_dict: New zone names dict
        """
        self.graph_widget.update_zone_names(zone_names_dict)
