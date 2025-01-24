import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
from datetime import datetime
import serial
import struct
import string
import serial.tools.list_ports

def extract_string(data):
    try:
        # Ensure data is binary-safe
        start_index = 2
        end_keyword = b'\x1A\x1E'
        value = struct.unpack('>H', data[:2])[0]
        # Find the position of the keyword 'ASSAY'
        end_index = data.find(end_keyword)

        if end_index == -1:
            data_len = len(data)
            raise ValueError(f"Keyword '0x1A0x1E' not found in data len={data_len}.")

        # Extract the substring from position 2 to the keyword
        result = data[start_index:end_index].decode('ascii', errors='ignore')
        return result

    except Exception as e:
        print(f"Error during string extraction: {e}")
        return None

def communicate_with_serial(port, baudrate, bytesize, stopbits, parity, timeout):
    try:
        # Open the serial connection
        with serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            stopbits=stopbits,
            parity=parity,
            timeout=timeout
        ) as ser:
            print(f"Connected to {port}")

            # Send binary value 0x11
            ser.write(b'D')
            print("Sent: 0x11")

            # Receive multiline string
            print("Receiving data...")
            received_data = extract_string(ser.read(657))
            ser.reset_input_buffer()

            print("Received data:")
            print(received_data)
            return received_data

    except serial.SerialException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def csv_to_matrix(csv_string):
    """
    Converts a string of comma-separated values into a matrix of numbers, ignoring the first value before the first comma on each line.

    Args:
        csv_string (str): The input string containing lines of comma-separated values.

    Returns:
        list[list[float]]: A matrix where each inner list represents a row of numbers.
    """
    try:
        # Split the string into lines
        lines = csv_string.strip().split('\n')

        # Convert each line into a list of floats, ignoring the first value (empty or not)
        matrix = [list(map(float, line.split(',')[1:])) for line in lines if line.strip()]

        return [[element / 1000 if isinstance(element, (float, int)) else element for element in row] for row in matrix]

    except ValueError as e:
        print(f"Error converting string to matrix: {e}")
        return None

class PlateReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EL800 96-Well Plate Reader")

        # Serial port settings
        self.serial_frame = tk.Frame(self.root)
        self.serial_frame.pack(pady=5)

        tk.Label(self.serial_frame, text="Serial Port:").grid(row=0, column=0, padx=5)
        self.serial_port_entry = tk.Entry(self.serial_frame, width=15)
        self.serial_port_entry.grid(row=0, column=1, padx=5)
        self.fill_first_available_port()

        tk.Label(self.serial_frame, text="Baud Rate:").grid(row=0, column=2, padx=5)
        self.baud_rate_combo = ttk.Combobox(
            self.serial_frame, width=10, values=[300, 1200, 2400, 4800, 9600, 19200]
        )
        self.baud_rate_combo.grid(row=0, column=3, padx=5)
        self.baud_rate_combo.set(9600)  # Default value

        tk.Label(self.serial_frame, text="Data Bits:").grid(row=1, column=0, padx=5)
        self.databits_combo = ttk.Combobox(self.serial_frame, width=10, values=[7, 8])
        self.databits_combo.grid(row=1, column=1, padx=5)
        self.databits_combo.set(8)  # Default value

        tk.Label(self.serial_frame, text="Parity:").grid(row=1, column=2, padx=5)
        self.parity_combo = ttk.Combobox(self.serial_frame, width=10, values=["No", "Even", "Odd"])
        self.parity_combo.grid(row=1, column=3, padx=5)
        self.parity_combo.set("No")  # Default value

        tk.Label(self.serial_frame, text="Stop Bits:").grid(row=2, column=0, padx=5)
        self.stopbits_combo = ttk.Combobox(self.serial_frame, width=10, values=[1, 2])
        self.stopbits_combo.grid(row=2, column=1, padx=5)
        self.stopbits_combo.set(1)  # Default value

        tk.Label(self.serial_frame, text="Handshake:").grid(row=2, column=2, padx=5)
        self.handshake_combo = ttk.Combobox(
            self.serial_frame, width=15, values=["No", "XON/XOFF", "RTS", "XON/XOFF+RTS"]
        )
        self.handshake_combo.grid(row=2, column=3, padx=5)
        self.handshake_combo.set("No")  # Default value

        # 96-well plate grid
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=10)

        # Add headers
        for col in range(12):
            tk.Label(
                self.grid_frame, text=f"{col + 1}", width=8, relief="ridge", bg="lightgray"
            ).grid(row=0, column=col + 1, padx=2, pady=2)

        for row in range(8):
            tk.Label(
                self.grid_frame, text=chr(65 + row), width=8, relief="ridge", bg="lightgray"
            ).grid(row=row + 1, column=0, padx=2, pady=2)

        self.well_labels = []
        for row in range(8):  # Rows A-H
            row_labels = []
            for col in range(12):  # Columns 1-12
                label = tk.Label(
                    self.grid_frame,
                    text="0.000",  # Default OD600 value
                    width=8,
                    height=2,
                    relief="ridge",
                    bg="white"
                )
                label.grid(row=row + 1, column=col + 1, padx=2, pady=2)
                row_labels.append(label)
            self.well_labels.append(row_labels)

        # Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.read_button = tk.Button(
            self.button_frame, text="Read", command=self.read_od600_values
        )
        self.read_button.pack(side="left", padx=5)

        self.close_button = tk.Button(
            self.button_frame, text="Close", command=self.root.quit
        )
        self.close_button.pack(side="left", padx=5)

        # Directory selector
        self.directory_frame = tk.Frame(self.root)
        self.directory_frame.pack(pady=10)

        tk.Label(self.directory_frame, text="Save Directory:").pack(side="left", padx=5)
        self.directory_entry = tk.Entry(self.directory_frame, width=40)
        self.directory_entry.pack(side="left", padx=5)
        self.browse_button = tk.Button(
            self.directory_frame, text="Browse", command=self.browse_directory
        )
        self.browse_button.pack(side="left", padx=5)

    def fill_first_available_port(self):
        ports = list(serial.tools.list_ports.comports())
        if ports:
            self.serial_port_entry.insert(0, ports[0].device)
        else:
            self.serial_port_entry.insert(0, "No ports found")

    def read_od600_values(self):
        # Get serial port settings from UI
        port = self.serial_port_entry.get()
        baudrate = int(self.baud_rate_combo.get())
        bytesize = serial.EIGHTBITS if self.databits_combo.get() == "8" else serial.SEVENBITS
        stopbits = serial.STOPBITS_TWO if self.stopbits_combo.get() == "2" else serial.STOPBITS_ONE
        parity = {
            "No": serial.PARITY_NONE,
            "Even": serial.PARITY_EVEN,
            "Odd": serial.PARITY_ODD
        }[self.parity_combo.get()]

        # Communicate with the serial device
        try:
            data = communicate_with_serial(port, baudrate, bytesize, stopbits, parity, timeout=5)

            if data:
                # Convert the received CSV data to a matrix
                matrix = csv_to_matrix(data)
                if matrix:
                    for row_idx, row in enumerate(matrix):
                        for col_idx, value in enumerate(row):
                            if row_idx < 8 and col_idx < 12:  # Ensure valid well range
                                self.well_labels[row_idx][col_idx].config(text=f"{value:.3f}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read OD600 values: {e}")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)

if __name__ == "__main__":
    root = tk.Tk()
    app = PlateReaderApp(root)
    root.mainloop()
