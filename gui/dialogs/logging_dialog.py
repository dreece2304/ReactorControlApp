"""Dialog for configuring temperature data logging."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QGridLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal
from pathlib import Path


class LoggingDialog(QDialog):
    """Dialog for configuring which zones to log and where to save."""

    # Emitted when logging settings change
    logging_started = Signal(set, str)  # (zones_set, base_path)
    logging_stopped = Signal()

    def __init__(self, device_ids, device_names, zone_names_dict,
                 current_path=None, active_zones=None, is_logging=False,
                 parent=None):
        """
        Initialize logging dialog.

        Args:
            device_ids: List of device IDs
            device_names: List of device display names
            zone_names_dict: Dict mapping device_id to zone names
            current_path: Current save path
            active_zones: Set of (device_id, zone) tuples currently being logged
            is_logging: Whether logging is currently active
            parent: Parent widget
        """
        super().__init__(parent)
        self.device_ids = device_ids
        self.device_names = device_names
        self.zone_names_dict = zone_names_dict
        self.current_path = current_path or ""
        self.active_zones = active_zones or set()
        self.is_logging = is_logging

        self.setWindowTitle("Temperature Logging")
        self.setMinimumWidth(500)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Save location
        path_group = QGroupBox("Save Location")
        path_layout = QHBoxLayout(path_group)

        self.path_edit = QLineEdit()
        self.path_edit.setText(str(self.current_path))
        self.path_edit.setPlaceholderText("Select folder for temperature logs...")
        path_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)

        layout.addWidget(path_group)

        # Zone selection
        zones_group = QGroupBox("Zones to Log")
        zones_layout = QGridLayout(zones_group)

        self.zone_checkboxes = {}  # (device_id, zone) -> QCheckBox

        row = 0
        for i, device_id in enumerate(self.device_ids):
            device_name = self.device_names[i] if i < len(self.device_names) else f"Device {device_id}"
            zone_names = self.zone_names_dict.get(device_id, [f"Zone {j+1}" for j in range(6)])

            # Device header
            header = QLabel(f"<b>{device_name}</b>")
            zones_layout.addWidget(header, row, 0, 1, 3)
            row += 1

            # Zone checkboxes (2 per row)
            col = 0
            for zone in range(1, 7):
                zone_name = zone_names[zone - 1] if zone <= len(zone_names) else f"Zone {zone}"
                checkbox = QCheckBox(zone_name)
                checkbox.setChecked((device_id, zone) in self.active_zones)
                self.zone_checkboxes[(device_id, zone)] = checkbox
                zones_layout.addWidget(checkbox, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            if col != 0:
                row += 1

        # Select all / none buttons
        btn_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        btn_row.addWidget(select_all_btn)

        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self._select_none)
        btn_row.addWidget(select_none_btn)
        btn_row.addStretch()

        zones_layout.addLayout(btn_row, row, 0, 1, 3)

        layout.addWidget(zones_group)

        # Status and control buttons
        control_layout = QHBoxLayout()

        self.status_label = QLabel()
        self._update_status()
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()

        if self.is_logging:
            self.toggle_btn = QPushButton("Stop Logging")
            self.toggle_btn.setStyleSheet("background-color: #ffcccc;")
        else:
            self.toggle_btn = QPushButton("Start Logging")
            self.toggle_btn.setStyleSheet("background-color: #ccffcc;")
        self.toggle_btn.clicked.connect(self._toggle_logging)
        control_layout.addWidget(self.toggle_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        control_layout.addWidget(close_btn)

        layout.addLayout(control_layout)

    def _browse_path(self):
        """Open folder browser dialog."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Log Folder",
            self.path_edit.text() or str(Path.home())
        )
        if path:
            self.path_edit.setText(path)

    def _select_all(self):
        """Select all zone checkboxes."""
        for checkbox in self.zone_checkboxes.values():
            checkbox.setChecked(True)

    def _select_none(self):
        """Deselect all zone checkboxes."""
        for checkbox in self.zone_checkboxes.values():
            checkbox.setChecked(False)

    def _update_status(self):
        """Update the status label."""
        if self.is_logging:
            count = len(self.active_zones)
            self.status_label.setText(f"<span style='color: green;'>Logging {count} zone(s)</span>")
        else:
            self.status_label.setText("<span style='color: gray;'>Logging stopped</span>")

    def _get_selected_zones(self):
        """Get set of selected zones."""
        zones = set()
        for (device_id, zone), checkbox in self.zone_checkboxes.items():
            if checkbox.isChecked():
                zones.add((device_id, zone))
        return zones

    def _toggle_logging(self):
        """Start or stop logging."""
        if self.is_logging:
            # Stop logging
            self.is_logging = False
            self.active_zones = set()
            self.logging_stopped.emit()
            self.toggle_btn.setText("Start Logging")
            self.toggle_btn.setStyleSheet("background-color: #ccffcc;")
        else:
            # Validate and start logging
            path = self.path_edit.text().strip()
            if not path:
                QMessageBox.warning(self, "No Path", "Please select a save location.")
                return

            zones = self._get_selected_zones()
            if not zones:
                QMessageBox.warning(self, "No Zones", "Please select at least one zone to log.")
                return

            # Verify path is writable
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Path Error", f"Cannot create directory:\n{e}")
                return

            self.is_logging = True
            self.active_zones = zones
            self.current_path = path
            self.logging_started.emit(zones, path)
            self.toggle_btn.setText("Stop Logging")
            self.toggle_btn.setStyleSheet("background-color: #ffcccc;")

        self._update_status()

    def get_settings(self):
        """
        Get current dialog settings.

        Returns:
            Dict with 'path', 'zones', 'is_logging'
        """
        return {
            'path': self.path_edit.text().strip(),
            'zones': self._get_selected_zones(),
            'is_logging': self.is_logging
        }
