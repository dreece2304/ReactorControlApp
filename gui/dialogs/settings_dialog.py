"""Dialog for application settings including COM port selection."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QFormLayout
)
from PySide6.QtCore import Signal
from utils.serial_utils import list_available_ports, is_port_available, format_port_display


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    # Emitted when port is changed: (new_port)
    port_changed = Signal(str)

    def __init__(self, current_port, parent=None):
        """
        Initialize settings dialog.

        Args:
            current_port: Currently configured port name
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_port = current_port
        self.selected_port = current_port

        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        self._setup_ui()
        self._refresh_ports()
        self._update_status()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # COM Port group
        port_group = QGroupBox("Serial Port")
        port_layout = QFormLayout(port_group)

        # Port selection combo with refresh button
        port_row = QHBoxLayout()

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(250)
        self.port_combo.currentTextChanged.connect(self._on_port_selected)
        port_row.addWidget(self.port_combo)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_ports)
        port_row.addWidget(self.refresh_button)

        port_layout.addRow("Port:", port_row)

        # Status indicator
        self.status_label = QLabel()
        port_layout.addRow("Status:", self.status_label)

        layout.addWidget(port_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._on_apply)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _refresh_ports(self):
        """Refresh the list of available ports."""
        self.port_combo.clear()

        # Get available ports
        ports = list_available_ports()

        # Track if current port is available
        current_available = False

        for port_name, description, hwid in ports:
            display_text = format_port_display(port_name)
            self.port_combo.addItem(display_text, port_name)

            if port_name == self.current_port:
                current_available = True

        # If current port is not in list, add it anyway (marked as unavailable)
        if not current_available and self.current_port:
            display_text = f"{self.current_port} (not available)"
            self.port_combo.addItem(display_text, self.current_port)

        # Select current port
        for i in range(self.port_combo.count()):
            if self.port_combo.itemData(i) == self.current_port:
                self.port_combo.setCurrentIndex(i)
                break

        self._update_status()

    def _on_port_selected(self, text):
        """Handle port selection change."""
        self.selected_port = self.port_combo.currentData()
        self._update_status()

    def _update_status(self):
        """Update the status indicator."""
        if not self.selected_port:
            self.status_label.setText("No port selected")
            self.status_label.setStyleSheet("color: orange;")
            self.apply_button.setEnabled(False)
            return

        if is_port_available(self.selected_port):
            if self.selected_port == self.current_port:
                self.status_label.setText("Currently connected")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("Available")
                self.status_label.setStyleSheet("color: blue;")
            self.apply_button.setEnabled(True)
        else:
            self.status_label.setText("Port not available")
            self.status_label.setStyleSheet("color: red;")
            self.apply_button.setEnabled(False)

    def _on_apply(self):
        """Handle apply button click."""
        if self.selected_port and self.selected_port != self.current_port:
            self.port_changed.emit(self.selected_port)
        self.accept()

    def get_selected_port(self):
        """
        Get the currently selected port.

        Returns:
            Port name string
        """
        return self.selected_port
