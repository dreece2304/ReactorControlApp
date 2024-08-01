import minimalmodbus
import serial

# Initialize the Modbus connection to the USB converter
port = 'COM3'  # Change this to your actual COM port
baudrate = 115200  # Make sure this matches your device settings


# Function to read a register from a Modbus device
def read_register(device_address, register_address):
    try:
        # Create an instrument instance for the device
        instrument = minimalmodbus.Instrument(port, device_address)
        instrument.serial.baudrate = baudrate
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1
        instrument.mode = minimalmodbus.MODE_RTU

        # Read register value
        value = instrument.read_register(register_address, 0)  # Change 0 if your register has decimals
        print(f"Device {device_address}, Register {register_address}: {value}")
    except Exception as e:
        print(f"Error communicating with device {device_address}: {e}")


# Test communication with device 1 (address 1) at register 40011
read_register(1, 10)  # Register 40011 corresponds to 10 in 0-based indexing

# Test communication with device 2 (address 2) at register 40011
read_register(2, 10)  # Register 40011 corresponds to 10 in 0-based indexing
