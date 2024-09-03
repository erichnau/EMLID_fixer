import serial
import serial.tools.list_ports
import time
import threading


def list_com_ports():
    return list(serial.tools.list_ports.comports())


def find_gga_port(ports):
    for port in ports:
        try:
            with serial.Serial(port.device, baudrate=9600, timeout=1) as ser:
                print(port.device)
                for _ in range(10):  # Try reading multiple lines
                    line = ser.readline().decode('ascii', errors='ignore').strip()
                    if line.startswith('$GPGGA'):
                        return port.device
        except Exception as e:
            print(f"Could not open port {port.device}: {e}")
            continue
    return None


def forward_data(source_port, dest_port):
    try:
        with serial.Serial(source_port, baudrate=9600, timeout=1) as src, \
                serial.Serial(dest_port, baudrate=9600, timeout=1) as dst:
            while True:
                data = src.read(1024)  # Read in chunks
                dst.write(data)
    except Exception as e:
        print(f"Error forwarding data: {e}")


def send_dummy_gga(port='COM4', baudrate=9600):
    # Define a dummy GGA string (NMEA format)
    dummy_gga = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"

    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            while True:
                ser.write(dummy_gga.encode('ascii'))  # Send the dummy GGA string
                print(f"Sent: {dummy_gga.strip()}")
                time.sleep(1)  # Wait for 1 second before sending the next line
    except serial.SerialException as e:
        print(f"Failed to open port {port}: {e}")


if __name__ == "__main__":
    # Start the send_dummy_gga function in a separate thread
    gga_thread = threading.Thread(target=send_dummy_gga, args=('COM4', 9600))
    gga_thread.daemon = True  # This ensures the thread will close when the main program exits
    gga_thread.start()

    # Continue with the main program
    ports = list_com_ports()
    print(ports)
    gps_port = find_gga_port(ports)
    print(gps_port)

    if gps_port:
        print(f"GGA data found on {gps_port}")
        # Assume the virtual COM port is COM9 (this should be configured separately)
        forward_data(gps_port, "COM1")
    else:
        print("No GGA data found on any COM port.")
