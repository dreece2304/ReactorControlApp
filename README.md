# ReactorControlApp

A PyQt5 GUI application for monitoring and controlling temperature zones on OMEGA CN616A Modbus RTU temperature controllers.

## Features

- Real-time temperature monitoring for multiple OMEGA CN616A controllers
- Support for multiple Modbus devices (default: 3 devices with 6 zones each)
- Configurable serial port, device IDs, and zone names
- Tabbed interface for easy navigation between devices
- Factory reset utility for device configuration

## Requirements

- Python 3.10+
- OMEGA CN616A temperature controller(s)
- RS-485 to USB adapter or serial port

## Installation

### Using pip (recommended)

```bash
# Clone the repository
git clone https://github.com/dreece2304/ReactorControlApp.git
cd ReactorControlApp

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Using Conda

```bash
conda env create -f environment.yml
conda activate reactor_control
```

## Configuration

Before running the application, edit `config.ini` to match your setup:

```ini
[serial]
# Serial port for Modbus communication
# Windows: COM5, COM6, etc.
# Linux: /dev/ttyUSB0, /dev/ttyACM0, etc.
# Mac: /dev/tty.usbserial-*, etc.
port = COM5
baudrate = 115200

[devices]
# Comma-separated list of Modbus device IDs
device_ids = 1, 2, 3

# Device display names (must match number of device_ids)
device_names = Chamber Temperatures, Local Reactants, Shared Lines

[display]
# Number of decimal points for temperature display
decimal_points = 0

# Update interval in milliseconds
update_interval_ms = 5000

[zone_names]
# Zone names for each device (6 zones per device)
1 = Chamber 1, Chamber 2, Chamber 3, Chamber 4, Chamber 5, Chamber 6
2 = THB, CB, DHB, BTY, EG, MPD
3 = SH1 - C1 and C2, SH1 - C3 and C4, SH1 - C5 and C6, SH2 - C1 and C2, SH2 - C3 and C4, SH2 - C5 and C6
```

### Finding Your Serial Port

**Windows:**
- Open Device Manager > Ports (COM & LPT)
- Look for your USB-to-Serial adapter (e.g., "USB Serial Port (COM5)")

**Linux:**
```bash
ls /dev/ttyUSB*
# or
ls /dev/ttyACM*
```

**Mac:**
```bash
ls /dev/tty.usb*
```

## Usage

### Running the GUI Application

```bash
python main.py
```

### Building a Standalone Executable (Windows)

```bash
pip install pyinstaller
pyinstaller TempControl.spec
```

The executable will be created in the `dist/` folder.

### Resetting a Device to Factory Defaults

```bash
# Reset device 1 on COM5 (default)
python -m controllers.reset_device

# Specify port and device ID
python -m controllers.reset_device --port COM6 --device-id 2
```

## Project Structure

```
ReactorControlApp/
├── main.py                      # Application entry point
├── config.ini                   # Configuration file
├── requirements.txt             # Python dependencies
├── environment.yml              # Conda environment
├── OMEGA_CN616A_Registers.json  # Device register configuration
├── gui/
│   ├── main_window.py          # Main application window
│   ├── zone_tab.py             # Tabbed device interface
│   └── zone_widget.py          # Zone temperature display
├── controllers/
│   ├── controller.py           # Temperature controller interface
│   ├── mock_controller.py      # Mock implementation for testing
│   └── reset_device.py         # Device reset utility
├── utils/
│   ├── config.py               # Configuration loader
│   └── modbus_communication.py # Modbus RTU communication
└── tests/                      # Unit tests
```

## Troubleshooting

### "Could not open port" error
- Verify the serial port is correct in `config.ini`
- Check that no other application is using the port
- On Linux, ensure you have permission to access serial ports:
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and back in for changes to take effect
  ```

### "Device not found" error
- Verify the Modbus device ID is correct
- Check RS-485 wiring (A/B polarity, termination)
- Ensure devices are powered on

### Temperature shows "Read error"
- Check serial cable connections
- Verify baudrate matches device configuration (default: 115200)
- Try reducing update interval if communication is unstable

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Submit a pull request
