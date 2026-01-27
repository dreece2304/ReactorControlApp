"""
Demo mode for ReactorControlApp - runs with simulated temperature data.

Usage:
    python demo.py

This runs the full application with a mock controller that generates
realistic temperature readings, allowing you to test all GUI features
without actual hardware connected.
"""
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt
from gui.zone_tab import ZoneTab
from gui.graph_panel import GraphPanel
from gui.dialogs import ZoneNamesDialog, SettingsDialog, LoggingDialog
from controllers.mock_controller import MockTemperatureController
from utils.config import load_config
from utils.temperature_history import TemperatureHistory
from utils.temperature_logger import TemperatureLogger
from PySide6.QtGui import QAction
import sys
import tempfile
import logging

logger = logging.getLogger(__name__)

# Demo logging path (use temp directory)
DEMO_LOG_PATH = tempfile.gettempdir()


class DemoMainWindow(QMainWindow):
    """MainWindow for demo mode with mock controller."""

    def __init__(self, config_file=None):
        """Initialize in demo mode with mock controller."""
        super().__init__()

        # Load configuration
        try:
            self.config = load_config(config_file)
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Configuration Error",
                                 f"Could not load configuration:\n{e}")
            raise

        self.port = "DEMO"
        self.device_ids = self.config.device_ids
        self.device_names = self.config.device_names
        self.zone_names_dict = self.config.zone_names_dict
        self.decimal_points = self.config.decimal_points
        self.update_interval_ms = self.config.update_interval_ms

        # Use mock controller
        self.controller = MockTemperatureController(
            port=self.port,
            device_ids=self.device_ids
        )

        # Create temperature history for graphing
        self.temperature_history = TemperatureHistory(self)

        # Create temperature logger for CSV export
        self.temperature_logger = TemperatureLogger(
            base_path=DEMO_LOG_PATH,
            device_names=self.device_names,
            zone_names_dict=self.zone_names_dict,
            parent=self
        )
        self.temperature_history.data_added.connect(self.temperature_logger.log_reading)

        # Set up UI
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_dock_panels()

        self.setWindowTitle("Temperature Controller [DEMO MODE]")
        self.resize(800, 600)
        self.show()

    def _setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        logging_action = QAction("Data Logging...", self)
        logging_action.triggered.connect(self._show_logging_dialog)
        file_menu.addAction(logging_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        zone_names_action = QAction("Edit Zone Names...", self)
        zone_names_action.triggered.connect(self._show_zone_names_dialog)
        edit_menu.addAction(zone_names_action)

        edit_menu.addSeparator()

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._show_settings_dialog)
        edit_menu.addAction(settings_action)

        # View menu
        self.view_menu = menubar.addMenu("View")

    def _setup_central_widget(self):
        """Set up the central widget (zone tabs)."""
        self.zone_tab = ZoneTab(
            self.controller,
            self.device_ids,
            self.device_names,
            self.zone_names_dict,
            decimal_points=self.decimal_points,
            update_interval_ms=self.update_interval_ms,
            temperature_history=self.temperature_history
        )
        self.setCentralWidget(self.zone_tab)

    def _setup_dock_panels(self):
        """Set up dockable panels."""
        self.graph_panel = GraphPanel(
            self.temperature_history,
            self.device_ids,
            self.device_names,
            self.zone_names_dict,
            self
        )
        self.addDockWidget(Qt.BottomDockWidgetArea, self.graph_panel)

        toggle_graph_action = self.graph_panel.toggleViewAction()
        toggle_graph_action.setText("Temperature Graph")
        self.view_menu.addAction(toggle_graph_action)

    def _show_logging_dialog(self):
        """Show the data logging configuration dialog."""
        dialog = LoggingDialog(
            self.device_ids,
            self.device_names,
            self.zone_names_dict,
            current_path=str(self.temperature_logger.base_path),
            active_zones=self.temperature_logger.get_active_zones(),
            is_logging=self.temperature_logger.is_logging,
            parent=self
        )
        dialog.logging_started.connect(self._on_logging_started)
        dialog.logging_stopped.connect(self._on_logging_stopped)
        dialog.exec()

    def _on_logging_started(self, zones, path):
        """Handle logging start."""
        from pathlib import Path
        self.temperature_logger.base_path = Path(path)
        self.temperature_logger.set_active_zones(zones)
        self.temperature_logger.start_logging()
        self.setWindowTitle("Temperature Controller [DEMO MODE] [LOGGING]")

    def _on_logging_stopped(self):
        """Handle logging stop."""
        self.temperature_logger.stop_logging()
        self.setWindowTitle("Temperature Controller [DEMO MODE]")

    def _show_zone_names_dialog(self):
        """Show the zone names editing dialog."""
        dialog = ZoneNamesDialog(
            self.device_ids,
            self.device_names,
            self.zone_names_dict,
            self
        )
        dialog.names_changed.connect(self._on_zone_names_changed)
        dialog.exec()

    def _on_zone_names_changed(self, new_names):
        """Handle zone names change."""
        for device_id, names in new_names.items():
            self.config.set_zone_names(device_id, names)
        self.config.save()
        self.config.reload()
        self.zone_names_dict = self.config.zone_names_dict
        self.zone_tab.update_zone_names(self.zone_names_dict)
        self.graph_panel.update_zone_names(self.zone_names_dict)
        self.temperature_logger.set_zone_names(self.zone_names_dict)

    def _show_settings_dialog(self):
        """Show settings dialog (disabled in demo mode)."""
        QMessageBox.information(
            self, "Demo Mode",
            "Port selection is disabled in demo mode.\n\n"
            "Run 'python main.py' to connect to real hardware."
        )

    def closeEvent(self, event):
        """Clean up resources."""
        if hasattr(self, 'temperature_logger') and self.temperature_logger.is_logging:
            self.temperature_logger.stop_logging()
        if hasattr(self, 'zone_tab'):
            self.zone_tab.stop_updates()
        if hasattr(self, 'controller'):
            self.controller.close()
        event.accept()


if __name__ == "__main__":
    print("=" * 50)
    print("ReactorControlApp - DEMO MODE")
    print("=" * 50)
    print("Using simulated temperature readings")
    print("No hardware required")
    print()
    print("Features to test:")
    print("  - Temperature display updates every 30s")
    print("  - Temperature graph (View menu)")
    print("  - Edit zone names (Edit menu)")
    print("  - Data logging to CSV (File menu)")
    print("=" * 50)
    print()

    app = QApplication(sys.argv)
    window = DemoMainWindow()
    sys.exit(app.exec())
