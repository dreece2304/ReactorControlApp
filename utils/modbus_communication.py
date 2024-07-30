import minimalmodbus

def read_register(port, address, register):
    instrument = minimalmodbus.Instrument(port, address)
    return instrument.read_register(register)

def write_register(port, address, register, value):
    instrument = minimalmodbus.Instrument(port, address)
    instrument.write_register(register, value)
