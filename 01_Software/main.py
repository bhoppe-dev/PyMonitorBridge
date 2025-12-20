import psutil
import time
import struct
# Import logic from our protocol module
from protocol import initSerialConnection, createMessage

# Configuration
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

# Initialize connection
serialConn = initSerialConnection(SERIAL_PORT, BAUD_RATE)

if serialConn is None:
    print("Serial port not available. Continuing in simulation mode.")


# Get CPU usage as payload (4-byte float)
def getCpuUsagePayload():
    cpuUsage = psutil.cpu_percent(interval=1)
    return struct.pack('f', cpuUsage)


# Get memory usage as payload (4-byte float)
def getMemoryUsagePayload():
    memoryUsage = psutil.virtual_memory().percent
    return struct.pack('f', memoryUsage)


def sendData():
    while True:
        # Collect hardware metrics
        cpuPayload = getCpuUsagePayload()
        memoryPayload = getMemoryUsagePayload()

        # Print current stats to console
        cpuVal = struct.unpack('f', cpuPayload)[0]
        memVal = struct.unpack('f', memoryPayload)[0]
        print(f"CPU: {cpuVal:.2f}% | RAM: {memVal:.2f}%")

        if serialConn is not None:
            # Create messages (0x01 for CPU, 0x02 for RAM)
            msgCpu = createMessage(0x01, cpuPayload)
            msgMemory = createMessage(0x02, memoryPayload)

            # Send CPU data
            print(f"Sending CPU Hex: {msgCpu.hex()}")
            serialConn.write(msgCpu)
            time.sleep(0.5)  # Short delay between packets

            # Send Memory data
            print(f"Sending RAM Hex: {msgMemory.hex()}")
            serialConn.write(msgMemory)

        else:
            print("Simulation: Serial port unavailable, skipping write.")

        time.sleep(1)


if __name__ == "__main__":
    try:
        sendData()
    except KeyboardInterrupt:
        if serialConn:
            serialConn.close()
        print("\nProgram stopped by user.")