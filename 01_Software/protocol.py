import serial
import serial.tools.list_ports
import time
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


# Function to automatically find the correct COM port
def discoverMcuPort(baudrate=9600):
    ports = serial.tools.list_ports.comports()
    print(f"Scanning {len(ports)} available ports...")

    for port in ports:
        print(f"Checking {port.device}...", end=" ", flush=True)
        tempConn = initSerialConnection(port.device, baudrate, timeout=2)

        if tempConn and tempConn.is_open:
            try:
                # Send discovery message (0xFF, empty payload)
                discoveryMsg = createMessage(0xFF, [])
                tempConn.write(discoveryMsg)

                # Wait a moment for the MCU to process and respond
                time.sleep(0.5)

                if tempConn.in_waiting > 0:
                    response = tempConn.read(tempConn.in_waiting).decode('utf-8', errors='ignore').strip()
                    print(f"FOUND! MCU responded with FW: {response}")
                    return tempConn  # Keep this connection open and return it
                else:
                    print("No response.")
                    tempConn.close()
            except Exception as e:
                print(f"Error during handshake: {e}")
                tempConn.close()

    return None