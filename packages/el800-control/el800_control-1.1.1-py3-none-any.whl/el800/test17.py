import serial
import sys
import struct


def extract_string(data):
    try:
        # Ensure data is binary-safe
        start_index = 2
        end_keyword = b'\x1A\x1E'
        value = struct.unpack('>H', data[:2])[0]
        # Find the position of the keyword 'ASSAY'
        end_index = data.find(end_keyword)
        
        if end_index == -1:
            data_len=len(data)
            raise ValueError(f"Keyword '0x1A0x1E' not found in data len={data_len}.")

        # Extract the substring from position 2 to the keyword
        result = data[start_index:end_index].decode('ascii', errors='ignore')
        return result

    except Exception as e:
        print(f"Error during string extraction: {e}")
        return None

def communicate_with_serial():
    port = "/dev/ttyUSB0"
    try:
        # Open the serial connection
        with serial.Serial(
            port=port,
            baudrate=9600, bytesize=serial.EIGHTBITS,
                           stopbits=serial.STOPBITS_TWO, parity=serial.PARITY_NONE, timeout=1,  # Timeout for reading in seconds
        ) as ser:
            print(f"Connected to {port}")
            
            # Send binary value 0x11
            ser.write(b'\x11')
            #ser.write(b'D')
            print("Sent: 0x11")
            
            # Receive multiline string
            print("Receiving data...")
            received_data =        data =extract_string( ser.read(657))
            ser.reset_input_buffer()

            
            print("Received data:")
            print(received_data)

    except serial.SerialException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":

    
    communicate_with_serial()
