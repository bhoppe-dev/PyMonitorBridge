import machine
import sys
import select
import struct
import time

# --- Configuration ---
FIRMWARE_VERSION = "RP2040-Slave-v1.0"

# Use the onboard LED. On Pico H/W, this is usually "LED".
# For older non-W Picos, it might be Pin 25.
led = machine.Pin("LED", machine.Pin.OUT)

# Ensure LED is off initially
led.value(0)

# Setup polling for USB Serial (stdin)
pollObj = select.poll()
pollObj.register(sys.stdin, select.POLLIN)


def triggerLedBlink(duration=0.05):
    """
    Blinks the LED for a short duration to indicate activity.
    Blocking delay is used here, but kept short (50ms) to not interrupt
    serial buffer at 9600 baud.
    """
    led.value(0)
    time.sleep(duration)
    led.value(1)


def calculateChecksum(data):
    """
    Calculates XOR checksum for the given byte data.
    Matches the Master logic: XOR of [Length, DataType, Payload].
    """
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum


def processMessage(dataType, payload):
    """
    Handles the received message based on DataType.
    """
    if dataType == 0xFF:
        # Handshake / Discovery Message
        # Respond with firmware version text
        print(FIRMWARE_VERSION)
        
    elif dataType == 0x01:
        # CPU Usage Data
        # Payload is a 4-byte float
        if len(payload) == 4:
            cpuVal = struct.unpack('f', payload)[0]
            # TODO: Implement MCU logic for CPU usage (e.g. display on OLED)
            pass
            
    elif dataType == 0x02:
        # Memory Usage Data
        # Payload is a 4-byte float
        if len(payload) == 4:
            memVal = struct.unpack('f', payload)[0]
            # TODO: Implement MCU logic for Memory usage
            pass


def receiveData():
    """
    Main loop to receive binary frames from PC.
    Frame format: [Length, DataType, Payload..., Checksum]
    """
    while True:
        # Check if data is available on USB Serial (timeout 10ms)
        if pollObj.poll(10):
            
            # 1. Read Length Byte
            lengthByte = sys.stdin.buffer.read(1)
            
            if not lengthByte:
                continue
                
            length = lengthByte[0]
            
            # 2. Read the body (DataType + Payload)
            # We expect exactly 'length' bytes
            body = sys.stdin.buffer.read(length)
            
            if len(body) != length:
                # Incomplete frame, discard
                continue
            
            # 3. Read Checksum Byte
            checksumByte = sys.stdin.buffer.read(1)
            if not checksumByte:
                continue
                
            receivedChecksum = checksumByte[0]
            
            # 4. Validate Checksum
            # Full frame for calculation is Length + Body
            fullFrameForCalc = lengthByte + body
            
            calculatedChecksum = calculateChecksum(fullFrameForCalc)
            
            if calculatedChecksum == receivedChecksum:
                # Valid packet received -> Visual Feedback
                triggerLedBlink()
                
                # Extract components
                dataType = body[0]
                payload = body[1:] # Slice the rest as payload
                
                processMessage(dataType, payload)
            else:
                # Checksum failed
                pass

if __name__ == "__main__":
    try:
        receiveData()
    except KeyboardInterrupt:
        # Ensure LED is off on exit
        led.value(0)