"""Temperature graph widget using matplotlib."""
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
)
from PySide6.QtCore import Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates


class TemperatureGraphWidget(QWidget):
    """Widget displaying a live temperature graph for a selected zone."""

    def __init__(self, temperature_history, device_ids, device_names, zone_names_dict,
                 parent=None):
        """
        Initialize the graph widget.

        Args:
            temperature_history: TemperatureHistory instance
            device_ids: List of device IDs
            device_names: List of device display names
            zone_names_dict: Dict mapping device ID to zone names
            parent: Parent widget
        """
        super().__init__(parent)
        self.temperature_history = temperature_history
        self.device_ids = device_ids
        self.device_names = device_names
        self.zone_names_dict = zone_names_dict

        self.selected_device_id = device_ids[0] if device_ids else None
        self.selected_zone = 1

        self._setup_ui()
        self._setup_plot()

        # Connect to history updates
        self.temperature_history.data_added.connect(self._on_data_added)

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Selection row
        selection_layout = QHBoxLayout()

        # Device selector
        selection_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        for i, device_id in enumerate(self.device_ids):
            name = self.device_names[i] if i < len(self.device_names) else f"Device {device_id}"
            self.device_combo.addItem(name, device_id)
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        selection_layout.addWidget(self.device_combo)

        selection_layout.addSpacing(20)

        # Zone selector
        selection_layout.addWidget(QLabel("Zone:"))
        self.zone_combo = QComboBox()
        self._update_zone_combo()
        self.zone_combo.currentIndexChanged.connect(self._on_zone_changed)
        selection_layout.addWidget(self.zone_combo)

        selection_layout.addStretch()

        layout.addLayout(selection_layout)

        # Matplotlib canvas
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def _setup_plot(self):
        """Set up the matplotlib plot."""
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Temperature (°C)')
        self.ax.grid(True, alpha=0.3)

        # Format x-axis for time
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.figure.autofmt_xdate()

        # Initialize empty line
        self.line, = self.ax.plot([], [], 'b-', linewidth=1.5)

        self._update_title()
        self.figure.tight_layout()

    def _update_title(self):
        """Update the plot title based on selection."""
        if self.selected_device_id is None:
            self.ax.set_title("No Device Selected")
            return

        device_idx = self.device_ids.index(self.selected_device_id) if self.selected_device_id in self.device_ids else 0
        device_name = self.device_names[device_idx] if device_idx < len(self.device_names) else f"Device {self.selected_device_id}"

        zone_names = self.zone_names_dict.get(self.selected_device_id, [f"Zone {i}" for i in range(1, 7)])
        zone_name = zone_names[self.selected_zone - 1] if self.selected_zone <= len(zone_names) else f"Zone {self.selected_zone}"

        self.ax.set_title(f"{device_name} - {zone_name}")

    def _update_zone_combo(self):
        """Update the zone combo box based on selected device."""
        self.zone_combo.blockSignals(True)
        self.zone_combo.clear()

        if self.selected_device_id is None:
            self.zone_combo.blockSignals(False)
            return

        zone_names = self.zone_names_dict.get(
            self.selected_device_id,
            [f"Zone {i}" for i in range(1, 7)]
        )

        for i, name in enumerate(zone_names):
            self.zone_combo.addItem(name, i + 1)

        self.zone_combo.blockSignals(False)

    def _on_device_changed(self, index):
        """Handle device selection change."""
        self.selected_device_id = self.device_combo.currentData()
        self._update_zone_combo()
        self.selected_zone = 1
        self._update_title()
        self._update_plot()

    def _on_zone_changed(self, index):
        """Handle zone selection change."""
        self.selected_zone = self.zone_combo.currentData() or 1
        self._update_title()
        self._update_plot()

    @Slot(int, int, float, object)
    def _on_data_added(self, device_id, zone, temperature, timestamp):
        """Handle new temperature data."""
        # Only update if this is for the selected device/zone
        if device_id == self.selected_device_id and zone == self.selected_zone:
            self._update_plot()

    def _update_plot(self):
        """Update the plot with current data."""
        if self.selected_device_id is None:
            return

        # Get history data
        timestamps = self.temperature_history.get_timestamps(
            self.selected_device_id, self.selected_zone
        )
        temperatures = self.temperature_history.get_temperatures(
            self.selected_device_id, self.selected_zone
        )

        if not timestamps:
            self.line.set_data([], [])
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw_idle()
            return

        # Update line data
        self.line.set_data(timestamps, temperatures)

        # Adjust axes
        self.ax.relim()
        self.ax.autoscale_view()

        # Set x-axis limits to show last hour (or available data)
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        min_time = min(timestamps)

        if min_time > one_hour_ago:
            self.ax.set_xlim(min_time, now + timedelta(seconds=30))
        else:
            self.ax.set_xlim(one_hour_ago, now + timedelta(seconds=30))

        self.canvas.draw_idle()

    def update_zone_names(self, zone_names_dict):
        """
        Update zone names for combo box.

        Args:
            zone_names_dict: New zone names dict
        """
        self.zone_names_dict = zone_names_dict
        current_zone = self.selected_zone
        self._update_zone_combo()

        # Restore selection if possible
        for i in range(self.zone_combo.count()):
            if self.zone_combo.itemData(i) == current_zone:
                self.zone_combo.setCurrentIndex(i)
                break

        self._update_title()
        self.figure.tight_layout()
        self.canvas.draw_idle()
