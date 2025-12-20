import serial
import struct

# Function to initialize serial port with error handling
def initSerialConnection(port, baudrate=9600, timeout=1):
    try:
        # Attempt to open the serial port
        serialConnection = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Successfully connected to {port}")
        return serialConnection
    except serial.SerialException as e:
        print(f"Error: Could not open port '{port}': {e}")
        return None

# Function to calculate XOR checksum
def calculateChecksum(data):
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum

# Function to create a message frame: [Length, DataType, Payload..., Checksum]
def createMessage(dataType, payload):
    # Length = DataType byte + Payload bytes
    # Note: We calculate checksum over [Length, DataType, Payload]
    length = 1 + len(payload)
    message = [length, dataType]

    # Add the payload (list of bytes)
    message.extend(payload)

    # Calculate and append checksum
    checksum = calculateChecksum(message)
    message.append(checksum)

    return bytearray(message)