from PySide6.QtWidgets import QMainWindow, QMessageBox, QMenuBar, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from .zone_tab import ZoneTab
from .graph_panel import GraphPanel
from .dialogs import ZoneNamesDialog, SettingsDialog, LoggingDialog
from controllers.controller import TemperatureController
from utils.config import load_config
from utils.temperature_history import TemperatureHistory
from utils.temperature_logger import TemperatureLogger
from utils.serial_utils import is_port_available
import logging

logger = logging.getLogger(__name__)

# Default logging path (Windows OneDrive path)
DEFAULT_LOG_PATH = r"C:\Users\dreec\OneDrive - UW\Documents - bergsmangroup\Data\HTReactorTemperature"


class MainWindow(QMainWindow):
    """Main application window for temperature monitoring."""

    def __init__(self, config_file=None):
        """
        Initialize main window.

        Args:
            config_file: Path to config.ini (uses default if None)
        """
        super(MainWindow, self).__init__()

        # Load configuration
        try:
            self.config = load_config(config_file)
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Configuration Error",
                                 f"Could not load configuration:\n{e}")
            raise

        self.port = self.config.port
        self.device_ids = self.config.device_ids
        self.device_names = self.config.device_names
        self.zone_names_dict = self.config.zone_names_dict
        self.decimal_points = self.config.decimal_points
        self.update_interval_ms = self.config.update_interval_ms

        # Check port availability at startup
        if not is_port_available(self.port):
            result = QMessageBox.warning(
                self, "Port Not Available",
                f"The configured port '{self.port}' is not available.\n\n"
                "Would you like to open Settings to select a different port?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if result == QMessageBox.Yes:
                self._show_settings_dialog_startup()

        # Initialize controller
        try:
            self.controller = TemperatureController(self.port, self.device_ids)
        except Exception as e:
            QMessageBox.critical(self, "Connection Error",
                                 f"Could not connect to devices on {self.port}:\n{e}")
            raise

        # Create temperature history for graphing
        self.temperature_history = TemperatureHistory(self)

        # Create temperature logger for CSV export
        self.temperature_logger = TemperatureLogger(
            base_path=DEFAULT_LOG_PATH,
            device_names=self.device_names,
            zone_names_dict=self.zone_names_dict,
            parent=self
        )
        # Connect logger to history data
        self.temperature_history.data_added.connect(self.temperature_logger.log_reading)

        # Set up UI
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_dock_panels()

        self.setWindowTitle("Temperature Controller")
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
        # Graph toggle action will be added after dock is created

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
        # Graph panel
        self.graph_panel = GraphPanel(
            self.temperature_history,
            self.device_ids,
            self.device_names,
            self.zone_names_dict,
            self
        )
        self.addDockWidget(Qt.BottomDockWidgetArea, self.graph_panel)

        # Add toggle action to View menu
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
        """Handle logging start from dialog."""
        from pathlib import Path
        self.temperature_logger.base_path = Path(path)
        self.temperature_logger.set_active_zones(zones)
        self.temperature_logger.start_logging()

        zone_count = len(zones)
        logger.info(f"Started logging {zone_count} zones to {path}")

        # Update window title to show logging status
        self.setWindowTitle("Temperature Controller [LOGGING]")

    def _on_logging_stopped(self):
        """Handle logging stop from dialog."""
        self.temperature_logger.stop_logging()
        logger.info("Stopped temperature logging")

        # Restore window title
        self.setWindowTitle("Temperature Controller")

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
        """Handle zone names change from dialog."""
        # Update config
        for device_id, names in new_names.items():
            self.config.set_zone_names(device_id, names)
        self.config.save()

        # Reload zone names from config
        self.config.reload()
        self.zone_names_dict = self.config.zone_names_dict

        # Update UI components
        self.zone_tab.update_zone_names(self.zone_names_dict)
        self.graph_panel.update_zone_names(self.zone_names_dict)

        # Update logger with new names
        self.temperature_logger.set_zone_names(self.zone_names_dict)

        logger.info("Zone names updated and saved")

    def _show_settings_dialog(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.port, self)
        dialog.port_changed.connect(self._on_port_changed)
        dialog.exec()

    def _show_settings_dialog_startup(self):
        """Show settings dialog during startup (before controller is created)."""
        dialog = SettingsDialog(self.port, self)

        if dialog.exec():
            new_port = dialog.get_selected_port()
            if new_port and new_port != self.port:
                self.port = new_port
                self.config.set_port(new_port)
                self.config.save()
                logger.info(f"Port changed to {new_port} during startup")

    def _on_port_changed(self, new_port):
        """Handle port change from settings dialog."""
        if new_port == self.port:
            return

        logger.info(f"Changing port from {self.port} to {new_port}")

        # Stop updates while we reconnect
        self.zone_tab.stop_updates()

        # Close old controller
        try:
            self.controller.close()
            logger.debug("Old controller connection closed")
        except Exception as e:
            logger.warning(f"Error closing old controller: {e}")

        # Create new controller
        try:
            self.controller = TemperatureController(new_port, self.device_ids)
            self.port = new_port

            # Update config
            self.config.set_port(new_port)
            self.config.save()

            # Update zone tab with new controller
            self.zone_tab.set_controller(self.controller)

            logger.info(f"Successfully connected to {new_port}")
            QMessageBox.information(
                self, "Connection Successful",
                f"Successfully connected to {new_port}"
            )

        except Exception as e:
            logger.error(f"Failed to connect to {new_port}: {e}")
            QMessageBox.critical(
                self, "Connection Error",
                f"Could not connect to devices on {new_port}:\n{e}\n\n"
                "Please check the connection and try again."
            )

            # Try to reconnect to old port
            try:
                self.controller = TemperatureController(self.port, self.device_ids)
                self.zone_tab.set_controller(self.controller)
                logger.info(f"Reconnected to original port {self.port}")
            except Exception as e2:
                logger.error(f"Failed to reconnect to original port: {e2}")
                QMessageBox.critical(
                    self, "Reconnection Failed",
                    f"Could not reconnect to original port {self.port}:\n{e2}\n\n"
                    "The application may not function correctly."
                )

    def closeEvent(self, event):
        """Clean up resources when window is closed."""
        # Stop logging
        if hasattr(self, 'temperature_logger') and self.temperature_logger.is_logging:
            self.temperature_logger.stop_logging()
            logger.info("Stopped logging on application close")

        # Stop all temperature updates
        if hasattr(self, 'zone_tab'):
            self.zone_tab.stop_updates()

        # Close controller connection
        if hasattr(self, 'controller'):
            try:
                self.controller.close()
                logger.debug("Controller connection closed")
            except Exception as e:
                logger.warning(f"Error closing controller: {e}")

        event.accept()
