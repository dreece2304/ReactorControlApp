from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLineEdit, QPushButton, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import datetime

class ZoneTab(QWidget):
    def __init__(self, zone_widget):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.times = []
        self.temperatures = []
        self.setpoint = None
        self.zone_widget = zone_widget

        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        # Connect the zone widget's temperature update to update the graph
        self.zone_widget.update_temperature_callback = self.update_graph

        self.y_scale_layout = QHBoxLayout()
        self.y_scale_input = QLineEdit()
        self.y_scale_input.setPlaceholderText("Y-axis max (default 200)")
        self.set_y_scale_button = QPushButton("Set Y-Axis Scale")
        self.set_y_scale_button.clicked.connect(self.set_y_scale)

        self.y_scale_layout.addWidget(self.y_scale_input)
        self.y_scale_layout.addWidget(self.set_y_scale_button)
        self.layout.addLayout(self.y_scale_layout)

        self.y_min = 0
        self.y_max = 200

    def update_graph(self):
        temp = self.zone_widget.controller.read_float(self.zone_widget.temperature_register)
        if temp is not None:
            self.times.append(datetime.datetime.now())
            self.temperatures.append(temp)
            self.ax.clear()
            self.ax.plot(self.times, self.temperatures, label='Temperature')
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Temperature (°C)')
            self.ax.legend()
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            if self.zone_widget.setpoint_input.text():
                self.setpoint = float(self.zone_widget.setpoint_input.text())
                self.ax.axhline(y=self.setpoint, color='r', linestyle='--', label='Setpoint')
            self.ax.set_ylim(self.y_min, self.y_max)
            self.figure.autofmt_xdate()
            self.canvas.draw()

    def set_y_scale(self):
        try:
            self.y_max = float(self.y_scale_input.text())
        except ValueError:
            self.y_max = 200
        self.ax.set_ylim(self.y_min, self.y_max)
        self.canvas.draw()
