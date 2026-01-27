"""Dialog for editing zone names."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QFormLayout
)
from PySide6.QtCore import Signal


class ZoneNamesDialog(QDialog):
    """Dialog for editing zone names for all devices."""

    # Emitted when names are saved: {device_id: [zone_names]}
    names_changed = Signal(dict)

    NUM_ZONES = 6

    def __init__(self, device_ids, device_names, zone_names_dict, parent=None):
        """
        Initialize zone names dialog.

        Args:
            device_ids: List of device IDs
            device_names: List of device display names
            zone_names_dict: Current zone names {device_id: [names]}
            parent: Parent widget
        """
        super().__init__(parent)
        self.device_ids = device_ids
        self.device_names = device_names
        self.zone_names_dict = zone_names_dict

        self.setWindowTitle("Edit Zone Names")
        self.setMinimumWidth(400)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Tab widget for each device
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Store references to line edits
        # Structure: {device_id: [QLineEdit, ...]}
        self.name_edits = {}

        for i, device_id in enumerate(self.device_ids):
            tab = QWidget()
            tab_layout = QFormLayout(tab)

            zone_names = self.zone_names_dict.get(
                device_id,
                [f"Zone {j + 1}" for j in range(self.NUM_ZONES)]
            )

            self.name_edits[device_id] = []

            for zone_num in range(self.NUM_ZONES):
                edit = QLineEdit()
                edit.setText(zone_names[zone_num] if zone_num < len(zone_names) else f"Zone {zone_num + 1}")
                edit.setMaxLength(50)
                tab_layout.addRow(f"Zone {zone_num + 1}:", edit)
                self.name_edits[device_id].append(edit)

            device_name = self.device_names[i] if i < len(self.device_names) else f"Device {device_id}"
            self.tab_widget.addTab(tab, device_name)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _on_save(self):
        """Handle save button click."""
        new_names = {}

        for device_id, edits in self.name_edits.items():
            names = [edit.text().strip() or f"Zone {i + 1}" for i, edit in enumerate(edits)]
            new_names[device_id] = names

        self.names_changed.emit(new_names)
        self.accept()

    def get_zone_names(self):
        """
        Get the current zone names from the dialog.

        Returns:
            Dict mapping device ID to list of zone names
        """
        new_names = {}
        for device_id, edits in self.name_edits.items():
            names = [edit.text().strip() or f"Zone {i + 1}" for i, edit in enumerate(edits)]
            new_names[device_id] = names
        return new_names
